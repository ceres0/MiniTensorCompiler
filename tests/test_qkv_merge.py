"""QKV packing semantics, guards, and preserved consumers."""

import numpy as np
import pytest
import tvm
from tvm import relax

from minicompiler.passes.merge_qkv import run_merge_qkv


def make_graph(batch=2, *, parameters=False, distinct_input=False, extra_consumer=False, dtype="float32", widths=(3, 3, 3)):
    rng = np.random.default_rng(0)
    weights = [rng.standard_normal((4, width), dtype=np.float32).astype(dtype) for width in widths]
    x = relax.Var("x", relax.TensorType((batch, 4), dtype))
    y = relax.Var("y", relax.TensorType((batch, 4), dtype))
    w = [relax.Var(f"w{i}", relax.TensorType((4, widths[i]), dtype)) for i in range(3)] if parameters else [relax.const(a) for a in weights]
    params = [x] + ([y] if distinct_input else []) + (w if parameters else [])
    bb = relax.BlockBuilder()
    with bb.function("main", params):
        with bb.dataflow():
            a = bb.emit(relax.op.matmul(x, w[0]))
            b = bb.emit(relax.op.matmul(y if distinct_input else x, w[1]))
            c = bb.emit(relax.op.matmul(x, w[2]))
            vals = [a, b, c]
            if extra_consumer:
                vals.append(bb.emit(relax.op.add(a, b)))
            out = bb.emit_output(relax.Tuple(vals))
        bb.emit_func_output(out)
    return bb.get(), weights


def execute(mod, x):
    vm = relax.VirtualMachine(tvm.compile(mod, target="llvm"), tvm.cpu())
    return [a.numpy() for a in vm["main"](tvm.runtime.tensor(x))]


@pytest.mark.parametrize("batch", [1, 2, 8, 32])
def test_packed_qkv_matches_reference_and_has_one_matmul(batch):
    mod, weights = make_graph(batch, extra_consumer=True)
    before = mod.script()
    rewritten, report = run_merge_qkv(mod, enabled=True, allowed_shapes=[(batch, 4, 3)])
    assert report["status"] == "ok" and report["rewrites"] == 1
    assert mod.script() == before
    assert before.count("R.matmul(") == 3
    assert rewritten.script().count("R.matmul(") == 1
    assert rewritten.script().count("R.strided_slice(") == 3
    x = np.random.default_rng(13).standard_normal((batch, 4), dtype=np.float32)
    actual = execute(rewritten, x)
    expected = execute(mod, x)
    for a, b in zip(actual, expected, strict=True):
        np.testing.assert_allclose(a, b, rtol=1e-4, atol=1e-5)
    np.testing.assert_allclose(actual[3], x @ weights[0] + x @ weights[1], rtol=1e-4, atol=1e-5)


def test_disabled_and_unmeasured_shapes_do_not_rewrite():
    mod, _ = make_graph()
    out, disabled = run_merge_qkv(mod)
    assert disabled["status"] == "disabled" and out.same_as(mod)
    out, report = run_merge_qkv(mod, enabled=True)
    assert report["rewrites"] == 0 and report["skipped_not_allowlisted"] == 1
    tvm.ir.assert_structural_equal(mod, out)


@pytest.mark.parametrize("options", [
    {"parameters": True}, {"distinct_input": True}, {"dtype": "float16"},
    {"widths": (3, 4, 3)}, {"batch": tvm.tirx.Var("batch", "int64")},
])
def test_unproved_cases_do_not_match(options):
    mod, _ = make_graph(**options)
    out, report = run_merge_qkv(mod, enabled=True, allowed_shapes=[(2, 4, 3)])
    assert report["status"] == "ok" and report["rewrites"] == 0
    tvm.ir.assert_structural_equal(mod, out)


def test_onnx_qkv_import_matches_ort(tmp_path):
    pytest.importorskip("torch")
    from models.export import export_model
    from minicompiler.frontend import load_and_summarize, import_relax
    from minicompiler.runtime.correctness import create_ort_runner, compare_outputs
    model = export_model("qkv", tmp_path / "qkv.onnx", batch=1)
    onnx, _ = load_and_summarize(model)
    mod = import_relax(onnx)
    out, report = run_merge_qkv(mod, enabled=True, allowed_shapes=[(1, 256, 256)])
    assert report["rewrites"] == 1
    x = np.random.default_rng(5).standard_normal((1, 256), dtype=np.float32)
    assert compare_outputs(execute(out, x), create_ort_runner(model)({"input": x}))["passed"]


def test_failed_normalization_rolls_back(monkeypatch):
    mod, _ = make_graph()
    def fail():
        raise RuntimeError("injected failure")
    monkeypatch.setattr(relax.transform, "Normalize", fail)
    out, report = run_merge_qkv(mod, enabled=True, allowed_shapes=[(2, 4, 3)])
    assert out.same_as(mod)
    assert report["status"] == "failed" and report["rewrites"] == 0
    assert report["attempted_rewrites"] == 1
    assert report["events"][0]["action"] == "rolled_back"
    assert "injected failure" in report["error"]


def test_experiment_matrix_emits_reproducible_shape_results(tmp_path):
    import json
    import subprocess
    import sys
    output = tmp_path / "matrix.json"
    proc = subprocess.run([sys.executable, "-m", "benchmarks.qkv_matrix", "--threads", "1",
                           "--warmup", "1", "--repeat", "2", "--rounds", "1",
                           "--output", str(output)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(output.read_text())
    assert len(report["results"]) == 6
    assert {(row["shape"]["M"], row["shape"]["K"]) for row in report["results"]} == {
        (m, k) for m in (1, 8, 32) for k in (256, 512)
    }
    assert all(row["correctness"]["passed"] and row["pass"]["rewrites"] == 1 for row in report["results"])
    assert all(row["inference"]["default"]["repetitions_per_round"] == 2 for row in report["results"])
