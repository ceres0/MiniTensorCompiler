"""End-to-end CPU correctness against ORT for real exported models."""

import numpy as np
import pytest

pytest.importorskip("torch", reason="install the models extra to export workloads")

from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.runtime.correctness import compare_outputs, create_ort_runner, make_inputs
from minicompiler.runtime.runner import build_runner
from models.export import export_model


@pytest.mark.parametrize("name,batch", [("mlp", 1), ("mlp", 8), ("mlp", 32), ("cnn", 1), ("cnn", 8)])
@pytest.mark.parametrize("mode", ["default", "nofusion"])
def test_compiled_models_match_ort(tmp_path, name, batch, mode):
    path = export_model(name, tmp_path / f"{name}.onnx", batch=batch, seed=17)
    model, summary = load_and_summarize(path)
    runner = build_runner(import_relax(model), mode=mode, target="llvm")
    ort = create_ort_runner(path, threads=1)
    generated = make_inputs(summary, seed=29)
    np.testing.assert_array_equal(generated["input"], make_inputs(summary, seed=29)["input"])
    shape = generated["input"].shape
    cases = [generated, {"input": np.zeros(shape, dtype=np.float32)},
             {"input": np.full(shape, 100, dtype=np.float32)},
             {"input": np.full(shape, -100, dtype=np.float32)}]
    for inputs in cases:
        actual = runner.outputs_to_numpy(runner.run_prepared(runner.prepare_inputs(inputs)))
        result = compare_outputs(actual, ort(inputs))
        assert result["passed"], (name, batch, mode, result)


@pytest.mark.parametrize("name,mode", [("mlp", "default"), ("cnn", "nofusion")])
def test_bench_cli_reports_real_measurements(tmp_path, name, mode):
    import json
    import subprocess
    import sys

    path = export_model(name, tmp_path / f"{name}.onnx", batch=1, seed=3)
    output = tmp_path / "benchmark.json"
    cmd = [sys.executable, "-m", "minicompiler", "bench", "--model", str(path),
           "--mode", mode, "--target", "llvm", "--threads", "1", "--seed", "7",
           "--warmup", "1", "--repeat", "2", "--rounds", "2", "--output", str(output)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(output.read_text())
    assert report["correctness"]["passed"] is True
    assert report["model"]["input_seed"] == 7
    assert report["model"]["inputs"][0]["dtype"] == "float32"
    assert report["pipeline"]["mode"] == mode
    assert report["environment"]["requested_threads"] == report["environment"]["tvm_runtime_threads"] == 1
    assert report["compilation"]["tvm_compile_ms"] > 0
    for system in ("tvm", "ort"):
        measurement = report["inference"][system]
        assert measurement["warmup"] == 1
        assert measurement["repetitions_per_round"] == measurement["rounds"] == 2
        assert len(measurement["samples_ms"]) == 2
        assert all(len(round_) == 2 for round_ in measurement["samples_ms"])
        assert measurement["median_ms"] > 0 and measurement["p95_ms"] > 0
    original = output.read_bytes()
    repeated = subprocess.run(cmd, text=True, capture_output=True)
    assert repeated.returncode != 0
    assert output.read_bytes() == original


@pytest.mark.parametrize("argument,value", [("--repeat", "0"), ("--rounds", "0"), ("--threads", "0"), ("--mode", "invalid"), ("--target", "cuda")])
def test_bench_cli_rejects_invalid_options(tmp_path, argument, value):
    import subprocess
    import sys

    output = tmp_path / "invalid.json"
    result = subprocess.run([sys.executable, "-m", "minicompiler", "bench", "--model", "unused.onnx",
                             "--output", str(output), argument, value], text=True, capture_output=True)
    assert result.returncode != 0
    assert not output.exists()
