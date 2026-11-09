"""A real small, non-divisible workload validates the ablation artifact."""
import json
from pathlib import Path
import subprocess
import sys


def test_ablation_vm_paths_and_report(tmp_path):
    root = Path(__file__).resolve().parents[1]
    out = tmp_path / "ablation"
    cmd = [sys.executable, "-m", "benchmarks.matmul_schedule", "--output-dir", str(out),
           "--shape", "5,7,11", "--threads", "2", "--warmup", "0", "--repeat", "1", "--rounds", "1"]
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((out / "report.json").read_text())
    assert report["environment"]["tvm_runtime_threads"] == 2
    record, = report["results"]
    assert record["shape"] == {"M": 5, "K": 7, "N": 11}
    assert set(record["stages"]) == {"default", "naive", "tile", "reorder", "parallel", "vectorize"}
    for name, stage in record["stages"].items():
        assert stage["correctness"]["passed"]
        assert stage["compile_ms"] > 0
        assert stage["inference"]["repetitions_per_round"] == 1
        assert stage["speedup_vs_tvm_default"] > 0
        filename = "default_tir.py" if name == "default" else f"{name}_tir.py"
        assert (out / "m5_k7_n11" / filename).exists()
    again = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert again.returncode != 0
