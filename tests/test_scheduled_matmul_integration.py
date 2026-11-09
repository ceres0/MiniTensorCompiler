"""Scheduled call_tir executes the same MLP as the original model and ORT."""
import numpy as np
import pytest
import tvm
from tvm import relax

from minicompiler.compiler.scheduled_matmul import run_scheduled_matmul
from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.runtime.correctness import create_ort_runner


def _run(mod, x):
    vm = relax.VirtualMachine(tvm.compile(mod, target="llvm", relax_pipeline="default"), tvm.cpu())
    return vm["main"](tvm.runtime.tensor(x)).numpy()


@pytest.mark.parametrize("batch", [1, 8, 32])
def test_scheduled_onnx_mlp_against_ort(tmp_path, batch):
    pytest.importorskip("torch")
    from models.export import export_model
    path = export_model("mlp", tmp_path / "model.onnx", batch=batch, seed=12)
    model, _ = load_and_summarize(path)
    original = import_relax(model)
    text = original.script()
    scheduled, report = run_scheduled_matmul(original)
    assert report["status"] == "ok", report
    assert report["rewrites"] == 2
    assert original.script() == text
    assert "T.vectorized(" in scheduled.script() and scheduled.script().count("R.call_tir(") == 2
    ref = create_ort_runner(path, threads=1)
    for seed in (0, 4):
        rng = np.random.default_rng(seed)
        x = rng.standard_normal((batch, 128), dtype=np.float32)
        np.testing.assert_allclose(_run(scheduled, x), ref({"input": x})[0], rtol=1e-4, atol=1e-5)
        np.testing.assert_allclose(_run(scheduled, x), _run(original, x), rtol=1e-4, atol=1e-5)


def test_float16_and_dynamic_shapes_are_not_scheduled():
    n = tvm.tirx.Var("n", "int64")
    for shape, dtype in [((2, 3), "float16"), ((n, 3), "float32")]:
        a = relax.Var("a", relax.TensorType(shape, dtype))
        b = relax.Var("b", relax.TensorType((3, 4), dtype))
        bb = relax.BlockBuilder()
        with bb.function("main", [a, b]):
            with bb.dataflow():
                out = bb.emit_output(relax.op.matmul(a, b))
            bb.emit_func_output(out)
        mod = bb.get()
        new, report = run_scheduled_matmul(mod)
        assert report["status"] == "ok" and report["rewrites"] == 0
        tvm.ir.assert_structural_equal(mod, new)


def test_invalid_stage_is_rejected():
    with pytest.raises(ValueError):
        run_scheduled_matmul(tvm.IRModule(), stage="invalid")
