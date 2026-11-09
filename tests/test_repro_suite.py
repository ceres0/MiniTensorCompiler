"""The one-command CPU suite runs real models and preserves failures."""
import json
import subprocess
import sys

import pytest

pytest.importorskip("torch", reason="install models extra for ONNX export")


def test_suite_produces_real_checked_reports_and_prevents_overwrite(tmp_path):
    out = tmp_path / "suite"
    cmd = [sys.executable, "-m", "benchmarks.run_suite", "--output-dir", str(out), "--threads", "1",
           "--warmup", "0", "--repeat", "1", "--rounds", "1", "--shape", "2,7,9", "--seed", "5"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout
    report = json.loads((out / "suite.json").read_text())
    assert report["status"] == "ok"
    assert len(report["steps"]) == 6
    assert all(s["returncode"] == 0 for s in report["steps"])
    assert report["parameters"]["matmul_shape"] == [2, 7, 9]
    assert report["packages"]["apache-tvm"] == "0.27.0.post1"
    for name in ("mlp", "cnn"):
        model_report = json.loads((out / f"{name}.json").read_text())
        assert model_report["correctness"]["passed"]
        assert model_report["correctness"]["default_vs_ort"]["passed"]
        assert model_report["inference"]["tvm"]["repetitions_per_round"] == 1
    schedule_report = json.loads((out / "matmul/report.json").read_text())
    assert all(s["correctness"]["passed"] for s in schedule_report["results"][0]["stages"].values())
    original = (out / "suite.json").read_bytes()
    assert subprocess.run(cmd, capture_output=True).returncode != 0
    assert (out / "suite.json").read_bytes() == original


def test_failure_produces_report_and_nonzero(tmp_path, monkeypatch):
    from benchmarks import run_suite
    from subprocess import CompletedProcess

    out = tmp_path / "failed"
    monkeypatch.setattr(run_suite.subprocess, "run", lambda *a, **k: CompletedProcess(a[0], 23, "", "injected error"))
    result = run_suite.main(["--output-dir", str(out)])
    assert result == 1
    report = json.loads((out / "suite.json").read_text())
    assert report["status"] == "failed"
    assert report["steps"][0]["returncode"] == 23
    assert "injected error" in (out / report["steps"][0]["stderr"]).read_text()
