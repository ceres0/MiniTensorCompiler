"""Checked, static FP32 ONNX model loading and TVM Relax import."""

from collections import Counter
from pathlib import Path

import onnx
from onnx import TensorProto, shape_inference


class OnnxImportError(ValueError):
    """Model validation or import failed; the underlying reason is retained."""


def _value_info(value):
    if not value.type.HasField("tensor_type"):
        raise OnnxImportError(f"Input {value.name!r}: only tensor inputs are supported")
    tensor = value.type.tensor_type
    if tensor.elem_type != TensorProto.FLOAT:
        raise OnnxImportError(f"Input {value.name!r}: only float32 is supported (ONNX dtype {tensor.elem_type})")
    if not tensor.HasField("shape"):
        raise OnnxImportError(f"Input {value.name!r}: unknown rank is not supported")
    dims = []
    for dim in tensor.shape.dim:
        if not dim.HasField("dim_value") or dim.dim_value <= 0:
            raise OnnxImportError(f"Input {value.name!r}: dimensions must be known positive integers")
        dims.append(dim.dim_value)
    return {"name": value.name, "shape": dims, "dtype": "float32"}


def load_and_summarize(path):
    """Load, validate, infer shapes and summarize an ONNX model.

    Runtime inputs must have fully static, positive dimensions and float32 dtype.
    Initializers are not runtime inputs. Returns the inferred model and a JSON-safe summary.
    """
    path = Path(path)
    try:
        model = onnx.load(str(path), load_external_data=True)
        onnx.checker.check_model(model)
        inferred = shape_inference.infer_shapes(model, strict_mode=True)
        onnx.checker.check_model(inferred)
    except Exception as exc:
        raise OnnxImportError(f"ONNX validation or shape inference failed for {path}: {exc}") from exc
    initializer_names = {initializer.name for initializer in inferred.graph.initializer}
    inputs = [_value_info(value) for value in inferred.graph.input if value.name not in initializer_names]
    nodes = [{"index": i, "name": node.name, "domain": node.domain or "ai.onnx", "op_type": node.op_type}
             for i, node in enumerate(inferred.graph.node)]
    summary = {
        "model": path.name,
        "ir_version": inferred.ir_version,
        "opsets": [{"domain": entry.domain or "ai.onnx", "version": entry.version} for entry in inferred.opset_import],
        "inputs": inputs,
        "outputs": [value.name for value in inferred.graph.output],
        "initializers": [{"name": x.name, "shape": list(x.dims), "dtype": TensorProto.DataType.Name(x.data_type)} for x in inferred.graph.initializer],
        "operator_counts": dict(sorted(Counter(node["op_type"] for node in nodes).items())),
        "nodes": nodes,
        "input_constraints": "Static positive shapes and float32 tensor inputs",
    }
    return inferred, summary


def import_relax(model, keep_params_in_input=False):
    """Import the validated model. Retained initializers live in main.attrs['params']."""
    from tvm.relax.frontend.onnx import from_onnx

    # The TVM importer dispatches by op_type alone. Reject custom domains rather
    # than accidentally interpreting a custom operator as a standard ONNX op.
    def check_domains(graph, graph_path="graph"):
        for i, node in enumerate(graph.node):
            if node.domain not in ("", "ai.onnx"):
                raise OnnxImportError(
                    f"Unsupported ONNX domain at {graph_path} node index={i} name={node.name!r} "
                    f"domain={node.domain} op={node.op_type}"
                )
            for attr in node.attribute:
                if attr.type == onnx.AttributeProto.GRAPH:
                    check_domains(attr.g, f"{graph_path}/{i}:{attr.name}")
                elif attr.type == onnx.AttributeProto.GRAPHS:
                    for j, subgraph in enumerate(attr.graphs):
                        check_domains(subgraph, f"{graph_path}/{i}:{attr.name}[{j}]")

    check_domains(model.graph)
    try:
        return from_onnx(model, keep_params_in_input=keep_params_in_input)
    except Exception as exc:
        message = str(exc)
        prefix = "The following operators are not supported for frontend ONNX: "
        detail = ""
        if prefix in message:
            unsupported = set(message.split(prefix, 1)[1].split(", "))
            matches = [f"index={i} name={node.name!r} domain={node.domain or 'ai.onnx'} op={node.op_type}"
                       for i, node in enumerate(model.graph.node) if node.op_type in unsupported]
            detail = "; unsupported nodes: " + "; ".join(matches)
        else:
            # Conversion failures can arise from a supported operator's attributes,
            # opset, or shape. TVM does not consistently expose the failing node.
            # List candidates without asserting that each is unsupported.
            candidates = [f"index={i} name={node.name!r} domain={node.domain or 'ai.onnx'} op={node.op_type}"
                          for i, node in enumerate(model.graph.node)]
            detail = "; candidate nodes (failure not localized): " + "; ".join(candidates)
        raise OnnxImportError(f"Relax ONNX import failed: {type(exc).__name__}: {message}{detail}") from exc
