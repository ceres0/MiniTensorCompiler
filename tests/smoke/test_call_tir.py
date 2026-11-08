"""Exercise the actual Relax-to-TensorIR boundary and LLVM execution."""

from pathlib import Path
import subprocess
import sys


def test_call_tir_example():
    example = Path(__file__).resolve().parents[2] / "examples" / "03_call_tir.py"
    completed = subprocess.run(
        [sys.executable, str(example)], check=True, capture_output=True, text=True
    )
    assert "R.call_tir" in completed.stdout
    assert "T.prim_func" in completed.stdout
    assert "@main:" in completed.stdout
    assert "call_tir output: [1. 2. 3. 4.]" in completed.stdout
