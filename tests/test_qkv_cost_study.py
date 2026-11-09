"""Cost study must preserve measured samples and never auto-enable a rule."""
import json
import os
import subprocess
import sys

from benchmarks.qkv_cost_study import candidate


def test_screen_rejects_small_sample_and_any_regression():
    win = {"default_median_ms": 1.2, "packed_median_ms": 1.0}
    assert not candidate([win] * 5)["candidate"]
    assert candidate([win] * 6)["candidate"]
    assert not candidate([win] * 5 + [{"default_median_ms": .9, "packed_median_ms": 1.0}])["candidate"]


def test_real_qkv_study_reports_costs_and_correctness(tmp_path):
    output = tmp_path / "study.json"
    cmd = [sys.executable, "-m", "benchmarks.qkv_cost_study", "--output", str(output), "--shape", "2,7,5", "--warmup", "1", "--repeat", "2", "--rounds", "2"]
    env = dict(os.environ, TVM_NUM_THREADS="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(output.read_text())
    record, = report["results"]
    assert record["shape"] == [2, 7, 5]
    assert all(item["passed"] for item in record["correctness"].values())
    assert record["logical_bytes"]["packed_intermediate"] == 2 * 3 * 5 * 4
    assert len(record["numpy_concat_ms"]["samples"]) == 2
    assert [r["order"][:2] for r in record["rounds"]] == [["default", "packed"], ["packed", "default"]]
    assert not record["screen"]["candidate"]
    assert subprocess.run(cmd, capture_output=True, text=True, env=env).returncode != 0
