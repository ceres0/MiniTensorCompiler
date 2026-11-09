"""CUDA MatMul schedule rejects invalid input and exposes thread mapping."""
import subprocess
import sys

import pytest

from minicompiler.schedules.matmul_cuda import make_cuda_matmul


def test_cuda_matmul_maps_output_and_guards_tail():
    script = make_cuda_matmul(7, 9, 35, threads=32).script()
    assert 'thread="blockIdx.y"' in script
    assert 'thread="blockIdx.x"' in script
    assert 'thread="threadIdx.x"' in script
    assert 'T.where(' in script
    assert 'T.init()' in script


@pytest.mark.parametrize("threads", [0, 1025, -1, True, 1.5])
def test_invalid_threads_rejected(threads):
    with pytest.raises(ValueError):
        make_cuda_matmul(2, 3, 4, threads)


def test_benchmark_bad_shape_fails_without_artifacts(tmp_path):
    output = tmp_path / "report"
    result = subprocess.run([sys.executable, "-m", "benchmarks.cuda_matmul", "--shape", "1,0,3", "--output-dir", str(output)], capture_output=True, text=True)
    assert result.returncode != 0
    assert not output.exists()


def test_cuda_end_to_end_if_available(tmp_path):
    import json
    import tvm
    try:
        available = tvm.runtime.enabled("cuda") and tvm.cuda(0).exist
    except Exception:
        available = False
    if not available:
        pytest.skip("CUDA device unavailable")
    output = tmp_path / "cuda"
    result = subprocess.run([sys.executable, "-m", "benchmarks.cuda_matmul", "--shape", "7,9,35", "--output-dir", str(output), "--warmup", "1", "--repeat", "2", "--rounds", "2"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((output / "report.json").read_text())
    for entry in report["results"][0]["stages"].values():
        assert entry["correctness"]["passed"]
        assert len(entry["inference"]["samples_ms"]) == 2
