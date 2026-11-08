"""The pass CLI emits reviewable before/after IR and an explicit report."""

import json
import subprocess
import sys

import numpy as np
import onnx
import pytest
from onnx import TensorProto, helper, numpy_helper


def make_model(path):
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, [2, 3, 4])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [3, 8])
    first = numpy_helper.from_array(np.array([6, 4], dtype="int64"), "first_shape")
    second = numpy_helper.from_array(np.array([3, 8], dtype="int64"), "second_shape")
    nodes = [helper.make_node("Reshape", ["input", "first_shape"], ["mid"], name="first"),
             helper.make_node("Reshape", ["mid", "second_shape"], ["output"], name="second")]
    model = helper.make_model(helper.make_graph(nodes, "reshape_chain", [x], [y], [first, second]),
                              opset_imports=[helper.make_opsetid("", 17)])
    onnx.save(model, path)


@pytest.mark.parametrize("enabled", [True, False])
def test_cli_dumps_ir_and_report(tmp_path, enabled):
    model = tmp_path / "chain.onnx"
    make_model(model)
    out = tmp_path / "out"
    cmd = [sys.executable, "-m", "minicompiler", "reshape", "--model", str(model), "--output-dir", str(out)]
    if not enabled:
        cmd.append("--disable")
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    before = (out / "00_relax_before.py").read_text()
    after = (out / "01_relax_after.py").read_text()
    report = json.loads((out / "02_reshape_report.json").read_text())
    assert report["enabled"] is enabled
    assert report["rewrites"] == (1 if enabled else 0)
    assert (before != after) is enabled
    repeated = subprocess.run(cmd, capture_output=True, text=True)
    assert repeated.returncode != 0
    assert (out / "01_relax_after.py").read_text() == after


def test_cli_reports_rollback_as_failure(tmp_path, monkeypatch, capsys):
    from minicompiler import cli
    from minicompiler.passes import redundant_reshape

    model = tmp_path / "chain.onnx"
    make_model(model)
    out = tmp_path / "out"
    monkeypatch.setattr(redundant_reshape, "run_redundant_reshape",
                        lambda mod, **_: (mod, {"status": "failed", "error": "injected"}))
    assert cli.main(["reshape", "--model", str(model), "--output-dir", str(out)]) == 1
    assert "injected" in capsys.readouterr().err
    assert json.loads((out / "02_reshape_report.json").read_text())["status"] == "failed"
    assert (out / "00_relax_before.py").read_text() == (out / "01_relax_after.py").read_text()
