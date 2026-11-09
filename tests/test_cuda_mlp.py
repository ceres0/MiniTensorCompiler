"""GPU model example fails closed; real CUDA integration runs only with a GPU."""

from types import SimpleNamespace
import subprocess
import sys

import numpy as np
import pytest
import tvm
from examples import cuda_mlp


def test_no_cuda_never_compiles(monkeypatch, capsys):
    monkeypatch.setattr(tvm.runtime, "enabled", lambda _: False)
    monkeypatch.setattr(tvm, "compile", lambda *a, **k: pytest.fail("unexpected CPU fallback"))
    assert cuda_mlp.main([]) == 1
    assert "CUDA unavailable" in capsys.readouterr().err


def test_gpu_visible_but_bad_model_fails_without_compiling(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(tvm.runtime, "enabled", lambda _: True)
    monkeypatch.setattr(tvm, "cuda", lambda _: SimpleNamespace(exist=True))
    monkeypatch.setattr(tvm, "compile", lambda *a, **k: pytest.fail("unexpected compilation"))
    assert cuda_mlp.main(["--model", str(tmp_path / "missing.onnx")]) == 1
    assert "CUDA ONNX execution failed" in capsys.readouterr().err


def test_gpu_compilation_failure_does_not_fall_back(monkeypatch, capsys):
    monkeypatch.setattr(tvm.runtime, "enabled", lambda _: True)
    monkeypatch.setattr(tvm, "cuda", lambda _: SimpleNamespace(exist=True))
    monkeypatch.setattr(cuda_mlp, "load_and_summarize", lambda _: (object(), {"inputs": [{"name": "x", "shape": [1], "dtype": "float32"}]}))
    monkeypatch.setattr(cuda_mlp, "import_relax", lambda *a, **k: {"main": SimpleNamespace(params=[object()])})
    monkeypatch.setattr(cuda_mlp, "create_ort_runner", lambda *a, **k: lambda x: [np.array([1], dtype="float32")])
    target = object()
    pipeline = object()
    monkeypatch.setattr(tvm.target, "Target", lambda name: target if name == "cuda" else pytest.fail("not CUDA"))
    monkeypatch.setattr(cuda_mlp.relax, "get_default_pipeline", lambda arg: pipeline if arg is target else pytest.fail("wrong target"))
    calls = []
    def fail_compile(*args, **kwargs):
        calls.append(kwargs)
        raise RuntimeError("GPU compile failed")
    monkeypatch.setattr(tvm, "compile", fail_compile)
    assert cuda_mlp.main(["--model", "unused.onnx"]) == 1
    assert calls == [{"target": target, "relax_pipeline": pipeline}]
    assert "GPU compile failed" in capsys.readouterr().err


def test_real_onnx_mlp_cuda_if_available():
    try:
        available = tvm.runtime.enabled("cuda") and tvm.cuda(0).exist
    except Exception:
        available = False
    if not available:
        pytest.skip("CUDA runtime or GPU unavailable; CUDA MLP execution was not tested")
    result = subprocess.run([sys.executable, "-m", "examples.cuda_mlp"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed vs ORT CPU" in result.stdout


def test_cuda_pipeline_lowers_real_mlp_without_gpu(tmp_path):
    from minicompiler.frontend import import_relax, load_and_summarize

    path = cuda_mlp.generate_demo_mlp(tmp_path / "mlp.onnx")
    model, _ = load_and_summarize(path)
    reference = cuda_mlp.create_ort_runner(path, threads=1)({"input": np.ones((1, 128), dtype=np.float32)})
    assert reference[0].shape == (1, 64)
    target = tvm.target.Target({"kind": "cuda", "arch": "sm_86"})
    lowered = tvm.relax.get_default_pipeline(target)(import_relax(model))
    assert "threadIdx.x" in lowered.script()
