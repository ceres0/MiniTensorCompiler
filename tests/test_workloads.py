"""The exported fixtures have the advertised graphs and match PyTorch."""

import numpy as np
import onnx
import onnxruntime as ort
import pytest

torch = pytest.importorskip("torch", reason="install the models extra to export workloads")

from models.export import WORKLOADS, export_model


@pytest.mark.parametrize(
    ("name", "operators"),
    [
        ("mlp", ["MatMul", "Add", "Relu", "MatMul", "Add"]),
        ("cnn", ["Conv", "Relu", "MaxPool", "Flatten", "MatMul", "Add"]),
        ("qkv", ["MatMul", "MatMul", "MatMul"]),
    ],
)
def test_export_is_static_and_matches_torch(tmp_path, name, operators):
    path = export_model(name, tmp_path / f"{name}.onnx", batch=2, seed=17)
    model = onnx.load(path)
    onnx.checker.check_model(model)
    assert [node.op_type for node in model.graph.node] == operators
    assert model.opset_import[0].version == 17
    model_type, shape, output_names = WORKLOADS[name]
    assert [dim.dim_value for dim in model.graph.input[0].type.tensor_type.shape.dim] == [2, *shape]
    assert model.graph.input[0].type.tensor_type.elem_type == onnx.TensorProto.FLOAT
    assert [value.name for value in model.graph.output] == list(output_names)
    torch.manual_seed(17)
    reference = model_type().eval()
    sample = torch.randn((2, *shape), dtype=torch.float32)
    with torch.no_grad():
        expected = reference(sample)
    if not isinstance(expected, tuple):
        expected = (expected,)
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    actual = session.run(None, {"input": sample.numpy()})
    for result, ref in zip(actual, expected, strict=True):
        np.testing.assert_allclose(result, ref.numpy(), rtol=1e-4, atol=1e-5)


def test_invalid_batch_rejected(tmp_path):
    with pytest.raises(ValueError, match="positive"):
        export_model("mlp", tmp_path / "invalid.onnx", batch=0)
