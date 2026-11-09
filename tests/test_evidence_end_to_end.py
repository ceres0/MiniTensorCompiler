"""Exercise one ONNX model through evidence, compiled artifact and ORT."""

import json

import numpy as np
import pytest

pytest.importorskip("torch", reason="install the models extra to export workloads")
from models.export import export_model
from minicompiler.runtime.correctness import create_ort_runner


@pytest.mark.parametrize("pass_mode,compile_mode", [("none", "default"), ("linear", "custom"), ("scheduled", "scheduled")])
def test_mlp_evidence_and_export_reload_match_ort(tmp_path, pass_mode, compile_mode):
    from minicompiler.compiler.evidence import export_evidence
    from minicompiler.compiler.artifacts import export_onnx_artifact, load_artifact

    model = export_model("mlp", tmp_path / "mlp.onnx", batch=2, seed=147)
    evidence_dir = tmp_path / "evidence"
    artifact_dir = tmp_path / "artifact"
    evidence_manifest, _, _ = export_evidence(model, evidence_dir, pass_mode=pass_mode)
    artifact_manifest = export_onnx_artifact(model, artifact_dir, mode=compile_mode)
    assert evidence_manifest["pass_mode"] == pass_mode
    assert artifact_manifest["model"]["weights"] == "embedded"
    assert artifact_manifest["pipeline"]["mode"] == compile_mode
    if pass_mode == "scheduled":
        assert evidence_manifest["scheduled_tir"]["available"]
        assert evidence_manifest["pass_report"]["schedule"]["rewrites"] == 2
        assert (evidence_dir / "07_scheduled_tir.py").stat().st_size > 0

    summary = json.loads((evidence_dir / "00_onnx_summary.json").read_text())
    assert summary["inputs"][0]["shape"] == [2, 128]
    assert summary["operator_counts"]["MatMul"] == 2
    for name in ("01_relax_imported.py", "02_relax_after_pass.py", "03_legalized_inspection.py", "04_vm.txt"):
        assert (evidence_dir / name).stat().st_size > 0
    assert "call_tir" in (evidence_dir / "03_legalized_inspection.py").read_text()
    assert (evidence_dir / "manifest.json").exists()
    # Backends lacking readable source must explicitly report unavailability.
    for key, name in (("llvm_ir", "05_llvm.ll"), ("assembly", "06_assembly.s")):
        path = evidence_dir / name
        if evidence_manifest["availability"][key]["available"]:
            assert path.exists()
            assert path.stat().st_size > 0
        else:
            assert evidence_manifest["availability"][key]["reason"]
            assert not path.exists()

    inputs = {"input": np.random.default_rng(29).standard_normal((2, 128), dtype=np.float32)}
    expected = create_ort_runner(model, threads=1)(inputs)
    model.unlink()  # The exported executable must not reopen the source model or weights.
    actual = load_artifact(artifact_dir).run(inputs)
    assert len(actual) == len(expected)
    for actual_item, expected_item in zip(actual, expected, strict=True):
        np.testing.assert_allclose(actual_item, expected_item, rtol=1e-4, atol=1e-5)


def test_invalid_model_and_existing_evidence_are_not_overwritten(tmp_path):
    from minicompiler.compiler.evidence import export_evidence

    bad = tmp_path / "broken.onnx"
    bad.write_bytes(b"not ONNX")
    with pytest.raises((ValueError, RuntimeError, OSError)):
        export_evidence(bad, tmp_path / "bad-evidence")
    model = export_model("mlp", tmp_path / "mlp.onnx", seed=22)
    path = tmp_path / "evidence"
    export_evidence(model, path)
    original = (path / "00_onnx_summary.json").read_bytes()
    with pytest.raises((ValueError, RuntimeError, OSError)):
        export_evidence(model, path)
    assert (path / "00_onnx_summary.json").read_bytes() == original


@pytest.mark.parametrize("pass_mode,compile_mode", [("linear", "custom"), ("scheduled", "scheduled")])
def test_cli_evidence_compile_run_roundtrip_and_no_overwrite(tmp_path, pass_mode, compile_mode):
    import os
    import subprocess
    import sys

    model = export_model("mlp", tmp_path / "cli-model.onnx", batch=1, seed=23)
    evidence = tmp_path / "evidence-cli"
    artifact = tmp_path / "artifact-cli"
    inputs_path = tmp_path / "input.npz"
    output = tmp_path / "output.npz"
    x = np.random.default_rng(4).standard_normal((1, 128), dtype=np.float32)
    np.savez(inputs_path, input=x)
    expected = create_ort_runner(model, threads=1)({"input": x})[0]
    env = dict(os.environ, TVM_NUM_THREADS="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")

    def run(*args):
        return subprocess.run([sys.executable, "-m", "minicompiler", *map(str, args)], env=env, capture_output=True, text=True)

    evidence_cmd = ("evidence", "--model", model, "--output-dir", evidence, "--pass-mode", pass_mode)
    compile_cmd = ("compile", "--model", model, "--target", "llvm", "--mode", compile_mode, "--output", artifact)
    for cmd in (evidence_cmd, compile_cmd):
        result = run(*cmd)
        assert result.returncode == 0, result.stdout + result.stderr
        assert run(*cmd).returncode != 0
    pass_report = json.loads((evidence / "manifest.json").read_text())["pass_report"]
    assert (pass_report["rewrites"] if pass_mode == "linear" else pass_report["schedule"]["rewrites"]) == (1 if pass_mode == "linear" else 2)
    model.unlink()
    run_cmd = ("run", "--artifact", artifact, "--inputs", inputs_path, "--output", output)
    result = run(*run_cmd)
    assert result.returncode == 0, result.stdout + result.stderr
    with np.load(output) as archive:
        assert archive.files == ["output"]
        np.testing.assert_allclose(archive["output"], expected, rtol=1e-4, atol=1e-5)
    before = output.read_bytes()
    assert run(*run_cmd).returncode != 0
    assert output.read_bytes() == before
    bad_input = tmp_path / "bad.npz"
    np.savez(bad_input, input=np.zeros((1, 127), dtype="float32"))
    bad_output = tmp_path / "bad-output.npz"
    assert run("run", "--artifact", artifact, "--inputs", bad_input, "--output", bad_output).returncode != 0
    assert not bad_output.exists()
