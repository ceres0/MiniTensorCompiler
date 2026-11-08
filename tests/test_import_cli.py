"""Exercise the three real workloads through the public import command."""

import json
import subprocess
import sys

import pytest

pytest.importorskip("torch", reason="install the models extra to export workloads")
from models.export import export_model


@pytest.mark.parametrize("name", ["mlp", "cnn", "qkv"])
@pytest.mark.parametrize("keep", [False, True], ids=["embedded", "parameters"])
def test_import_workload(tmp_path, name, keep):
    model = export_model(name, tmp_path / f"{name}.onnx", seed=5)
    output = tmp_path / "imported"
    cmd = [sys.executable, "-m", "minicompiler", "import", "--model", str(model), "--output-dir", str(output)]
    if keep:
        cmd.append("--keep-params-in-input")
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    summary = json.loads((output / "00_onnx_summary.json").read_text())
    inspection = json.loads((output / "02_relax_inspection.json").read_text())
    assert summary["inputs"][0]["dtype"] == "float32"
    assert summary["keep_params_in_input"] is keep
    assert summary["operator_counts"]
    assert inspection["relax_calls"] > 0
    assert "def main" in (output / "01_relax_imported.py").read_text()
    repeat = subprocess.run(cmd, capture_output=True, text=True)
    assert repeat.returncode != 0
    assert "already exist" in repeat.stderr


def test_bad_model_fails_without_creating_artifacts(tmp_path):
    model = tmp_path / "broken.onnx"
    model.write_bytes(b"not an ONNX model")
    out = tmp_path / "out"
    result = subprocess.run([sys.executable, "-m", "minicompiler", "import", "--model", str(model), "--output-dir", str(out)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Import failed" in result.stderr
    assert not out.exists()
