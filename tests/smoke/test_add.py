"""Exercise the real CPU compiler and exported executable, not a mock."""

from pathlib import Path
import subprocess
import sys


def test_add_example_compiles_executes_and_reloads():
    example = Path(__file__).resolve().parents[2] / "examples" / "00_add.py"
    completed = subprocess.run(
        [sys.executable, str(example)], check=True, capture_output=True, text=True
    )
    assert "export/reload passed" in completed.stdout
