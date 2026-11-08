"""Regression tests for CPU runner input binding and supported targets."""

import numpy as np
import onnx
import onnxruntime as ort
import pytest
from onnx import TensorProto, helper

from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.runtime.runner import build_runner


def test_original_onnx_input_names_bind_after_sanitization(tmp_path):
    name = "input/value:0"
    inputs = [helper.make_tensor_value_info(name, TensorProto.FLOAT, [1, 2])]
    outputs = [helper.make_tensor_value_info("out", TensorProto.FLOAT, [1, 2])]
    graph = helper.make_graph([helper.make_node("Relu", [name], ["out"])], "named", inputs, outputs)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)], ir_version=10)
    path = tmp_path / "name.onnx"
    onnx.save(model, path)
    model, summary = load_and_summarize(path)
    mod = import_relax(model)
    runner = build_runner(mod, onnx_input_names=[v["name"] for v in summary["inputs"]])
    value = np.array([[-1, 2]], dtype="float32")
    result = runner.outputs_to_numpy(runner.run_prepared(runner.prepare_inputs({name: value})))
    expected = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"]).run(None, {name: value})
    np.testing.assert_array_equal(result[0], expected[0])
    with pytest.raises(ValueError, match="parameter count"):
        build_runner(mod, onnx_input_names=[])
