"""Compile a static ONNX model for NVIDIA CUDA and compare with ORT CPU.

This example uses TVM's target-specific CUDA Relax pipeline. It does not alter
or enable CUDA in the CPU-only project benchmark and artifact CLI.
"""

import argparse
from pathlib import Path
import sys
import tempfile

import numpy as np
import onnx
import tvm
from onnx import TensorProto, helper, numpy_helper
from tvm import relax

from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.runtime.correctness import compare_outputs, create_ort_runner, make_inputs


def generate_demo_mlp(path):
    """Generate a small deterministic ONNX workload without requiring PyTorch."""
    rng = np.random.default_rng(0)
    params = []
    for name, shape in (("w1", (128, 256)), ("b1", (256,)),
                        ("w2", (256, 64)), ("b2", (64,))):
        value = rng.standard_normal(shape, dtype=np.float32) * np.float32(0.05)
        params.append(numpy_helper.from_array(value, name))
    nodes = [helper.make_node("MatMul", ["input", "w1"], ["mm1"]),
             helper.make_node("Add", ["mm1", "b1"], ["bias1"]),
             helper.make_node("Relu", ["bias1"], ["hidden"]),
             helper.make_node("MatMul", ["hidden", "w2"], ["mm2"]),
             helper.make_node("Add", ["mm2", "b2"], ["output"])]
    graph = helper.make_graph(nodes, "cuda_mlp", [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 128])],
                              [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 64])], params)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    # ONNX's latest IR version may exceed the pinned ONNX Runtime's support;
    # use the minimum version required by the declared standard opset.
    model.ir_version = helper.find_min_ir_version_for(model.opset_import)
    onnx.checker.check_model(model)
    onnx.save(model, path)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, help="static FP32 ONNX model; default generates a small demo MLP")
    parser.add_argument("--seed", type=int, default=0, help="fixed input seed (default 0)")
    args = parser.parse_args(argv)
    if args.seed < 0:
        parser.error("--seed must be nonnegative")
    try:
        if not tvm.runtime.enabled("cuda"):
            print("CUDA unavailable: TVM CUDA runtime is not enabled", file=sys.stderr)
            return 1
        device = tvm.cuda(0)
        if not device.exist:
            print("CUDA unavailable: no accessible NVIDIA CUDA device", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"CUDA unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    try:
        with tempfile.TemporaryDirectory(prefix="minicompiler-cuda-mlp-") as tmp:
            path = args.model
            if path is None:
                path = generate_demo_mlp(Path(tmp) / "mlp.onnx")
            model, summary = load_and_summarize(path)
            module = import_relax(model, keep_params_in_input=False)
            inputs = make_inputs(summary, seed=args.seed)
            reference = create_ort_runner(path, threads=1)(inputs)
            # The ONNX frontend preserves input ordering even when names are sanitized.
            if len(module["main"].params) != len(summary["inputs"]):
                raise ValueError("ONNX inputs do not match Relax function parameters")
            target = tvm.target.Target("cuda")
            pipeline = relax.get_default_pipeline(target)
            executable = tvm.compile(module, target=target, relax_pipeline=pipeline)
            vm = relax.VirtualMachine(executable, device)
            arrays = [tvm.runtime.tensor(inputs[item["name"]], device=device) for item in summary["inputs"]]
            result = vm["main"](*arrays)
            device.sync()
            if isinstance(result, tvm.runtime.Tensor):
                actual = [result.numpy()]
            else:
                actual = [value.numpy() for value in result]
            correctness = compare_outputs(actual, reference)
            if not correctness["passed"]:
                print(f"CUDA output mismatch vs ORT CPU: {correctness}", file=sys.stderr)
                return 1
            print(f"TVM CUDA ONNX execution passed vs ORT CPU: {correctness}")
            return 0
    except Exception as exc:
        print(f"CUDA ONNX execution failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
