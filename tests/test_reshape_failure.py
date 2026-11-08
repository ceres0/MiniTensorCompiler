"""A failed pass must not expose partially rewritten IR as a successful result."""

import tvm
from tvm import relax

import minicompiler.passes.redundant_reshape as reshape_pass


def make_module():
    x = relax.Var("x", relax.TensorType((2, 3), "float32"))
    bb = relax.BlockBuilder()
    with bb.function("main", [x]):
        with bb.dataflow():
            intermediate = bb.emit(relax.op.reshape(x, (6,)))
            out = bb.emit_output(relax.op.reshape(intermediate, (3, 2)))
        bb.emit_func_output(out)
    return bb.get()


def test_exception_after_rewrite_rolls_back_and_reports_error(monkeypatch):
    mod = make_module()
    original_text = mod.script()
    rewrite = reshape_pass.rewrite_call

    def fails_after_rewrite(*args):
        rewrite(*args)
        raise RuntimeError("injected pass failure")

    monkeypatch.setattr(reshape_pass, "rewrite_call", fails_after_rewrite)
    output, report = reshape_pass.run_redundant_reshape(mod)
    assert output.same_as(mod)
    assert mod.script() == original_text
    assert report["status"] == "failed"
    assert "injected pass failure" in report["error"]
    assert report["attempted_rewrites"] == 1
    assert report["rewrites"] == 0
    assert report["events"][0]["action"] == "rolled_back"


def test_status_for_success_and_disabled():
    mod = make_module()
    result, report = reshape_pass.run_redundant_reshape(mod)
    assert report["status"] == "ok" and report["error"] is None
    assert report["attempted_rewrites"] == report["rewrites"] == 1
    assert not result.same_as(mod)
    result, report = reshape_pass.run_redundant_reshape(mod, enabled=False)
    assert result.same_as(mod)
    assert report["status"] == "disabled" and report["error"] is None
    assert report["attempted_rewrites"] == report["rewrites"] == 0
