"""CUDA smoke must fail closed when CUDA is unavailable; real GPU is optional."""

import subprocess
import sys
from types import SimpleNamespace

import pytest
import tvm

from examples import cuda_add


def test_disabled_cuda_runtime_never_compiles_or_falls_back(monkeypatch, capsys):
    monkeypatch.setattr(tvm.runtime, "enabled", lambda _: False)
    def unexpected(*args, **kwargs):
        pytest.fail("compilation or device lookup must not occur without CUDA runtime")
    monkeypatch.setattr(tvm, "compile", unexpected)
    monkeypatch.setattr(tvm, "cuda", unexpected)
    assert cuda_add.main() == 1
    assert "CUDA unavailable" in capsys.readouterr().err


def test_missing_cuda_device_never_compiles_or_falls_back(monkeypatch, capsys):
    monkeypatch.setattr(tvm.runtime, "enabled", lambda _: True)
    monkeypatch.setattr(tvm, "cuda", lambda _: SimpleNamespace(exist=False))
    monkeypatch.setattr(tvm, "compile", lambda *args, **kwargs: pytest.fail("unexpected fallback compile"))
    assert cuda_add.main() == 1
    assert "no accessible NVIDIA CUDA device" in capsys.readouterr().err


def test_cuda_build_failure_does_not_fall_back_to_cpu(monkeypatch, capsys):
    monkeypatch.setattr(tvm.runtime, "enabled", lambda _: True)
    monkeypatch.setattr(tvm, "cuda", lambda _: SimpleNamespace(exist=True))
    calls = []
    def fail_compile(*args, **kwargs):
        calls.append(kwargs.get("target"))
        raise RuntimeError("injected CUDA build error")
    monkeypatch.setattr(tvm, "compile", fail_compile)
    assert cuda_add.main() == 1
    assert calls == ["cuda"]
    assert "injected CUDA build error" in capsys.readouterr().err


def test_real_cuda_add_when_device_available():
    try:
        available = tvm.runtime.enabled("cuda") and tvm.cuda(0).exist
    except Exception:
        available = False
    if not available:
        pytest.skip("CUDA runtime or GPU is unavailable; no GPU execution was tested")
    result = subprocess.run([sys.executable, "-m", "examples.cuda_add"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "compiled and passed on GPU" in result.stdout
