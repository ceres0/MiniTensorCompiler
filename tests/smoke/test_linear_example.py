"""Structural and executable evidence for the linear fusion example."""

import json
from pathlib import Path
import subprocess
import sys


def test_linear_example_emits_tir_and_runs_both_pipelines(tmp_path):
    example = Path(__file__).resolve().parents[2] / "examples" / "05_linear_fusion.py"
    result = subprocess.run([sys.executable, str(example), "--output-dir", str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads((tmp_path / "04_report.json").read_text())
    assert report["rewrites"] == 1 and report["max_abs_error"] < 1e-5
    assert report["inspection"]["unfused_tir_primfunc_count"] == 3
    assert report["inspection"]["fused_tir_primfunc_count"] == 1
    assert report["inspection"]["runtime_kernel_invocations"] is None
    before = (tmp_path / "02_tir_before.py").read_text()
    after = (tmp_path / "03_tir_after.py").read_text()
    assert before.count("R.call_tir(") == 3
    assert after.count("R.call_tir(") == 1
    assert "sblock_alloc_buffer" in after
