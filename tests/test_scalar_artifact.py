"""Rank-zero input must remain rank zero through export and VM invocation."""

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper

from minicompiler.compiler.artifacts import export_onnx_artifact, load_artifact


def test_scalar_input_roundtrips_artifact_and_matches_ort(tmp_path):
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, [])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [])
    bias = numpy_helper.from_array(np.array(1.5, dtype="float32"), name="bias")
    graph = helper.make_graph([helper.make_node("Add", ["input", "bias"], ["output"])],
                              "scalar", [x], [y], [bias])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 10  # ORT 1.31 does not yet accept ONNX's newest IR version.
    path = tmp_path / "scalar.onnx"
    onnx.save(model, path)
    manifest = export_onnx_artifact(path, tmp_path / "artifact")
    assert manifest["model"]["inputs"][0]["shape"] == []
    value = np.asarray(2.0, dtype="float32")
    expected = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"]).run(None, {"input": value})
    actual = load_artifact(tmp_path / "artifact").run({"input": value})
    assert actual[0].shape == ()
    np.testing.assert_allclose(actual[0], expected[0], rtol=1e-4, atol=1e-5)
