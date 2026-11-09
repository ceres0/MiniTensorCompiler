"""Controlled MatMul benchmark contract and Linux integration."""
import json
import argparse
import os
from pathlib import Path
import subprocess
import sys

import pytest

from benchmarks.cpu_deep_dive import parse_cpus, parse_triple


def test_parse_inputs():
    assert parse_cpus("2,3") == [2, 3]
    assert parse_triple("5,7,11") == (5, 7, 11)
    with pytest.raises(argparse.ArgumentTypeError):
        parse_cpus("1,1")
    with pytest.raises(argparse.ArgumentTypeError):
        parse_triple("1,0,1")


@pytest.mark.skipif(not hasattr(os, "sched_getaffinity"), reason="requires Linux affinity")
def test_linux_interleaved_benchmark(tmp_path):
    cpus = sorted(os.sched_getaffinity(0))[:2]
    out = tmp_path / "result"
    cmd = [sys.executable, "-m", "benchmarks.cpu_deep_dive", "--output-dir", str(out),
           "--cpus", ",".join(map(str, cpus)), "--threads", str(len(cpus)),
           "--shape", "5,7,11", "--warmup", "1", "--repeat", "2", "--rounds", "2"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads((out / "report.json").read_text())
    assert report["environment"]["affinity_actual"] == cpus
    assert report["environment"]["tvm_runtime_threads"] == len(cpus)
    record = report["results"][0]
    assert len(record["round_order"]) == 2
    for stage in record["stages"].values():
        assert stage["correctness"]["passed"]
        assert len(stage["samples_ms"]) == 2
        assert all(len(samples) == 2 for samples in stage["samples_ms"])
        assert stage["median_ms"] > 0
    assert subprocess.run(cmd, capture_output=True).returncode != 0
