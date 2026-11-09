"""Native CPU artifacts preserve embedded parameters across export/load."""
import json

import numpy as np
import onnx
import pytest
from onnx import TensorProto, helper, numpy_helper

from minicompiler.compiler.artifacts import export_onnx_artifact, load_artifact
from minicompiler.runtime.correctness import create_ort_runner


def model_file(tmp_path):
    x = helper.make_tensor_value_info("input/data", TensorProto.FLOAT, [2, 3])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [2, 2])
    w = numpy_helper.from_array(np.arange(6, dtype="float32").reshape(3, 2) / 10, "weight")
    b = numpy_helper.from_array(np.array([1.0, -1.0], dtype="float32"), "bias")
    nodes = [helper.make_node("MatMul", [x.name, "weight"], ["m"]),
             helper.make_node("Add", ["m", "bias"], ["a"]),
             helper.make_node("Relu", ["a"], ["output"])]
    model = helper.make_model(helper.make_graph(nodes, "test", [x], [y], [w, b]), opset_imports=[helper.make_opsetid("", 17)])
    # Keep IR at a version supported by the installed ORT.
    model.ir_version = 10
    path = tmp_path / "model.onnx"
    onnx.save_model(model, str(path), save_as_external_data=True, all_tensors_to_one_file=True,
                    location="weights.bin", size_threshold=0)
    return path


@pytest.mark.parametrize("mode", ["default", "nofusion", "custom"])
def test_artifact_roundtrip_with_embedded_external_weights(tmp_path, mode):
    path = model_file(tmp_path)
    inputs = {"input/data": np.arange(6, dtype="float32").reshape(2, 3)}
    reference = create_ort_runner(path)(inputs)
    out = tmp_path / "artifact"
    manifest = export_onnx_artifact(path, out, mode=mode)
    assert manifest["model"]["weights"] == "embedded"
    assert manifest["pipeline"]["mode"] == mode
    assert manifest["executable"]["size_bytes"] > 0
    # No source ONNX or external weight file is required after compilation.
    path.unlink()
    (tmp_path / "weights.bin").unlink()
    result = load_artifact(out).run(inputs)
    for actual, expected in zip(result, reference, strict=True):
        np.testing.assert_allclose(actual, expected, rtol=1e-4, atol=1e-5)
    with pytest.raises(ValueError, match="shape or dtype"):
        load_artifact(out).run({"input/data": inputs["input/data"].astype("float64")})
    with pytest.raises(ValueError, match="names"):
        load_artifact(out).run({"wrong": inputs["input/data"]})
    with pytest.raises(FileExistsError):
        export_onnx_artifact(path, out)


def test_mismatched_library_and_platform_are_rejected_before_loading(tmp_path):
    path = model_file(tmp_path)
    out = tmp_path / "artifact"
    export_onnx_artifact(path, out)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["runtime"]["machine"] = "not-the-host"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="platform"):
        load_artifact(out)
    manifest["runtime"]["machine"] = __import__("platform").machine()
    manifest["executable"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="does not match"):
        load_artifact(out)


def test_scheduled_mlp_artifact_roundtrip(tmp_path):
    pytest.importorskip("torch")
    from models.export import export_model
    from minicompiler.runtime.correctness import compare_outputs, make_inputs
    from minicompiler.frontend import load_and_summarize

    path = export_model("mlp", tmp_path / "mlp.onnx", batch=8, seed=4)
    _, summary = load_and_summarize(path)
    inputs = make_inputs(summary, seed=9)
    expected = create_ort_runner(path)(inputs)
    out = tmp_path / "scheduled"
    manifest = export_onnx_artifact(path, out, mode="scheduled")
    assert manifest["reshape_pass"]["status"] == "ok"
    assert manifest["schedule"]["status"] == "ok"
    assert manifest["schedule"]["rewrites"] >= 1
    assert manifest["pipeline"]["mode"] == "scheduled"
    assert compare_outputs(load_artifact(out).run(inputs), expected)["passed"]


def test_scheduled_artifact_rejects_no_eligible_matmul(tmp_path):
    x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [2, 3])
    y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [2, 3])
    model = helper.make_model(helper.make_graph([helper.make_node("Relu", ["x"], ["y"])], "relu", [x], [y]), opset_imports=[helper.make_opsetid("", 17)])
    path = tmp_path / "relu.onnx"
    onnx.save(model, path)
    with pytest.raises(ValueError, match="no eligible matmul"):
        export_onnx_artifact(path, tmp_path / "scheduled", mode="scheduled")
    assert not (tmp_path / "scheduled").exists()
