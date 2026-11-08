"""The public rewrite example must compile and run both versions on LLVM."""

import json
from pathlib import Path
import subprocess
import sys


def test_reshape_example_compiles_and_saves_ir(tmp_path):
    example = Path(__file__).resolve().parents[2] / "examples" / "02_relax_pass.py"
    output = tmp_path / "reshape"
    result = subprocess.run([sys.executable, str(example), "--output-dir", str(output)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "LLVM VM outputs match" in result.stdout
    report = json.loads((output / "report.json").read_text())
    assert report["rewrites"] == 1
    before, after = (output / "before.py").read_text(), (output / "after.py").read_text()
    assert before.count("R.reshape(") == 2
    assert after.count("R.reshape(") == 1
