"""Public CLI checks for linear graph rewriting and benchmark reporting."""

import json
import subprocess
import sys

import pytest

pytest.importorskip("torch", reason="install models extra to export workloads")
from models.export import export_model


@pytest.fixture
def mlp_model(tmp_path):
    return export_model("mlp", tmp_path / "mlp.onnx", seed=18)


def run(*args):
    return subprocess.run([sys.executable, "-m", "minicompiler", *map(str, args)],
                          text=True, capture_output=True)


@pytest.mark.parametrize("keep", [False, True], ids=["embedded", "weight_inputs"])
@pytest.mark.parametrize("enabled", [False, True], ids=["disabled", "enabled"])
def test_linear_cli_modes_and_no_overwrite(mlp_model, tmp_path, keep, enabled):
    out = tmp_path / "linear"
    args = ["linear", "--model", mlp_model, "--output-dir", out]
    if keep:
        args.append("--keep-params-in-input")
    if not enabled:
        args.append("--disable")
    result = run(*args)
    assert result.returncode == 0, result.stderr
    report_path = out / "02_linear_report.json"
    report = json.loads(report_path.read_text())
    assert report["keep_params_in_input"] is keep
    assert report["enabled"] is enabled
    assert report["status"] == ("ok" if enabled else "disabled")
    assert report["rewrites"] == int(enabled)
    if enabled:
        assert report["matches"] >= 1
        assert any(event["action"] == "accepted" for event in report["events"])
    before = (out / "00_relax_before.py").read_text()
    after = (out / "01_relax_after.py").read_text()
    assert (before != after) is enabled
    original = report_path.read_bytes()
    repeated = run(*args)
    assert repeated.returncode != 0
    assert report_path.read_bytes() == original


def test_custom_benchmark_compares_tvm_default_and_ort(mlp_model, tmp_path):
    report_path = tmp_path / "bench.json"
    args = ["bench", "--model", mlp_model, "--target", "llvm", "--mode", "custom", "--threads", "1",
            "--warmup", "1", "--repeat", "2", "--rounds", "2", "--seed", "9", "--output", report_path]
    result = run(*args)
    assert result.returncode == 0, result.stderr
    report = json.loads(report_path.read_text())
    assert report["pipeline"]["mode"] == "custom"
    assert report["model"]["input_seed"] == 9
    assert report["model"]["weights"] == "embedded ONNX initializers"
    assert report["custom_pass"]["status"] == "ok"
    assert report["custom_pass"]["rewrites"] == 1
    assert report["correctness"]["passed"]
    assert report["correctness"]["default_vs_ort"]["passed"]
    for key in ("tvm", "tvm_default", "ort"):
        item = report["inference"][key]
        assert item["warmup"] == 1
        assert item["repetitions_per_round"] == item["rounds"] == 2
        assert len(item["samples_ms"]) == 2
        assert all(len(values) == 2 for values in item["samples_ms"])
        assert item["median_ms"] > 0 and item["p95_ms"] > 0
    timing = report["compilation"]
    assert timing["custom_pass_ms"] > 0 and timing["tvm_default_compile_ms"] > 0 and timing["tvm_compile_ms"] > 0
    assert timing["onnx_load_check_shape_inference_ms"] > 0 and timing["relax_import_ms"] > 0
    assert timing["pass_timing"]["by_pass"]["LegalizeOps"]["calls"] >= 1
    assert timing["pass_timing"]["incomplete_passes"] == 0
    assert timing["codegen_ms"] is None and timing["schedule_ms"] is None
    assert report["ir_stats"]["tir_primfunc_counts"]
    assert report["ir_stats"]["runtime_kernel_invocations"] is None
    assert report["inference"]["default_over_custom_speedup"] > 0
    original = report_path.read_bytes()
    repeated = run(*args)
    assert repeated.returncode != 0
    assert report_path.read_bytes() == original


def test_custom_benchmark_zero_matches_has_no_speedup_claim(tmp_path):
    model = export_model("qkv", tmp_path / "qkv.onnx", seed=18)
    out = tmp_path / "no-match.json"
    result = run("bench", "--model", model, "--target", "llvm", "--mode", "custom", "--threads", "1",
                 "--warmup", "1", "--repeat", "2", "--rounds", "2", "--output", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["custom_pass"]["status"] == "ok"
    assert report["custom_pass"]["rewrites"] == 0
    assert report["correctness"]["passed"]
    assert report["inference"]["default_over_custom_speedup"] is None
