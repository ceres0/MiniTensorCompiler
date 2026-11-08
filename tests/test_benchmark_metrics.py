import numpy as np
import onnx
from onnx import TensorProto, helper
import pytest

from minicompiler.runtime.correctness import make_inputs, create_ort_runner, compare_outputs
from minicompiler.profiling.benchmark import measure


def test_deterministic_inputs():
    summary = {"inputs": [{"name": "x", "shape": [2, 3], "dtype": "float32"}]}
    x = make_inputs(summary, seed=42)["x"]
    np.testing.assert_array_equal(x, make_inputs(summary, seed=42)["x"])
    assert x.dtype == np.float32
    assert not np.array_equal(x, make_inputs(summary, seed=43)["x"])


def test_compare_multiple_outputs_and_nonfinite():
    ref = [np.array([0, 1, -2], dtype=np.float32), np.array([1e5], dtype=np.float32)]
    ok = compare_outputs(ref, ref)
    assert ok["passed"] and ok["max_abs_error"] == ok["rmse"] == 0
    bad = compare_outputs([ref[0] + 0.1, ref[1]], ref)
    assert not bad["passed"] and bad["max_abs_error"] > 0 and bad["rmse"] > 0
    nonfinite = compare_outputs([np.array([np.nan, 1, -2]), ref[1]], ref)
    assert not nonfinite["passed"] and nonfinite["max_abs_error"] is None
    with pytest.raises(ValueError, match="shape mismatch"):
        compare_outputs([np.zeros((3, 1)), ref[1]], ref)
    with pytest.raises(ValueError, match="count mismatch"):
        compare_outputs(ref[:1], ref)


def test_ort_cpu_runner_real_onnx(tmp_path):
    x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [2])
    y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [2])
    graph = helper.make_graph([helper.make_node("Relu", ["x"], ["y"])], "relu", [x], [y])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)], ir_version=10)
    path = tmp_path / "relu.onnx"
    onnx.save(model, path)
    run = create_ort_runner(path, threads=1)
    actual = run({"x": np.array([-1, 1], dtype=np.float32)})
    np.testing.assert_array_equal(actual[0], [0, 1])
    with pytest.raises(ValueError):
        create_ort_runner(path, threads=0)


def test_measure_counts_rounds_and_samples():
    calls = []
    result = measure(lambda: calls.append(1), warmup=2, repeat=3, rounds=2)
    assert len(calls) == 8
    assert [len(row) for row in result["samples_ms"]] == [3, 3]
    assert result["median_ms"] >= 0 and result["p95_ms"] >= result["median_ms"]
    for args in ((-1, 1, 1), (0, 0, 1), (0, 1, 0)):
        with pytest.raises(ValueError):
            measure(lambda: None, *args)
