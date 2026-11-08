import numpy as np
import onnx
import pytest
from onnx import TensorProto, helper, numpy_helper

from minicompiler.frontend import OnnxImportError, import_relax, load_and_summarize


def make_model(tmp_path, shape=(1, 3), dtype=TensorProto.FLOAT, custom=False):
    x = helper.make_tensor_value_info("input", dtype, shape)
    y = helper.make_tensor_value_info("output", dtype, shape)
    weight = numpy_helper.from_array(np.array([1, 2, 3], dtype=np.float32), "weight")
    node = helper.make_node("Add", ["input", "weight"], ["output"], name="named_add", domain="example.custom" if custom else "")
    opsets = [helper.make_opsetid("", 17)]
    if custom:
        opsets.append(helper.make_opsetid("example.custom", 1))
    model = helper.make_model(helper.make_graph([node], "test", [x], [y], [weight]), opset_imports=opsets)
    path = tmp_path / "model.onnx"
    onnx.save(model, path)
    return path


def test_summary_and_parameter_modes(tmp_path):
    model, summary = load_and_summarize(make_model(tmp_path))
    assert summary["inputs"] == [{"name": "input", "shape": [1, 3], "dtype": "float32"}]
    assert summary["operator_counts"] == {"Add": 1}
    assert summary["nodes"][0]["name"] == "named_add"
    embedded = import_relax(model)
    retained = import_relax(model, keep_params_in_input=True)
    assert len(embedded["main"].params) == 1
    main = retained["main"]
    assert len(main.params) == 2
    assert int(main.attrs["num_input"]) == 1
    assert len(main.attrs["params"]) == 1
    np.testing.assert_array_equal(main.attrs["params"][0].numpy(), [1, 2, 3])


@pytest.mark.parametrize("shape,dtype", [(("batch", 3), TensorProto.FLOAT), ((1, 3), TensorProto.INT64)])
def test_unsupported_input_rejected(tmp_path, shape, dtype):
    with pytest.raises(OnnxImportError, match="Input"):
        load_and_summarize(make_model(tmp_path, shape, dtype))


def test_custom_domain_not_silently_treated_as_standard_add(tmp_path):
    model, _ = load_and_summarize(make_model(tmp_path, custom=True))
    with pytest.raises(OnnxImportError, match="index=0.*named_add.*example.custom.*Add"):
        import_relax(model)


def test_unknown_op_identifies_node(tmp_path):
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3])
    node = helper.make_node("Mystery", ["input"], ["output"], name="mystery_node")
    model = helper.make_model(helper.make_graph([node], "test", [x], [y]), opset_imports=[helper.make_opsetid("", 17)])
    with pytest.raises(OnnxImportError, match="index=0.*mystery_node.*Mystery"):
        import_relax(model)


def test_valid_onnx_unsupported_operator_reports_actual_node(tmp_path):
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3])
    node = helper.make_node("Bernoulli", ["input"], ["output"], name="random_node")
    model = helper.make_model(helper.make_graph([node], "test", [x], [y]), opset_imports=[helper.make_opsetid("", 17)])
    path = tmp_path / "bernoulli.onnx"
    onnx.save(model, path)
    checked, _ = load_and_summarize(path)
    with pytest.raises(OnnxImportError, match="unsupported nodes:.*index=0.*random_node.*Bernoulli"):
        import_relax(checked)


def test_conversion_failure_reports_candidates_without_claiming_unsupported(tmp_path, monkeypatch):
    import tvm.relax.frontend.onnx as tvm_onnx

    model, _ = load_and_summarize(make_model(tmp_path))
    def fail(*args, **kwargs):
        raise ValueError("unsupported axis value")
    monkeypatch.setattr(tvm_onnx, "from_onnx", fail)
    with pytest.raises(OnnxImportError) as error:
        import_relax(model)
    assert "unsupported axis value" in str(error.value)
    assert "candidate nodes (failure not localized)" in str(error.value)
    assert "index=0 name='named_add' domain=ai.onnx op=Add" in str(error.value)


def test_valid_det_node_reports_unsupported_operator(tmp_path):
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, [2, 2])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [])
    node = helper.make_node("Det", ["input"], ["output"], name="determinant")
    model = helper.make_model(helper.make_graph([node], "test", [x], [y]), opset_imports=[helper.make_opsetid("", 17)])
    path = tmp_path / "det.onnx"
    onnx.save(model, path)
    checked, _ = load_and_summarize(path)
    with pytest.raises(OnnxImportError, match="unsupported nodes:.*index=0.*determinant.*Det"):
        import_relax(checked)
