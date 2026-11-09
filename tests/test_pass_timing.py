"""Pass timings and static counts must describe the actual single compilation."""
import numpy as np
import tvm
from tvm import relax

from minicompiler.profiling.pass_timing import PassTimer


def test_instrument_real_compilation_and_static_count():
    a = relax.Var("a", relax.TensorType((2, 3), "float32"))
    b = relax.Var("b", relax.TensorType((2, 3), "float32"))
    builder = relax.BlockBuilder()
    with builder.function("main", [a, b]):
        with builder.dataflow():
            out = builder.emit_output(relax.op.add(a, b))
        builder.emit_func_output(out)
    timer = PassTimer()
    assert timer.snapshot()["static_ir_snapshots"] == []
    with tvm.transform.PassContext(opt_level=2, instruments=[timer]):
        executable = tvm.compile(builder.get(), target="llvm", relax_pipeline="default")
    report = timer.snapshot()
    assert report["incomplete_passes"] == 0
    assert report["by_pass"]["LegalizeOps"]["calls"] == 1
    assert report["by_pass"]["LegalizeOps"]["inclusive_ms"] > 0
    assert any(x["after_pass"] == "LegalizeOps" and x["tir_primfunc_count"] >= 1 for x in report["static_ir_snapshots"])
    assert report["runtime_kernel_invocations"] is None
    assert all(0 <= x["exclusive_ms"] <= x["inclusive_ms"] for x in report["events"])
    assert any(x["depth"] > 0 for x in report["events"])
    vm = relax.VirtualMachine(executable, tvm.cpu())
    a_value = np.arange(6, dtype="float32").reshape(2, 3)
    b_value = np.ones((2, 3), dtype="float32")
    out = vm["main"](tvm.runtime.tensor(a_value), tvm.runtime.tensor(b_value)).numpy()
    np.testing.assert_array_equal(out, a_value + b_value)


def test_empty_timer_does_not_claim_unobserved_passes():
    result = PassTimer().snapshot()
    assert result["by_pass"] == {}
    assert result["static_ir_snapshots"] == []
    assert result["runtime_kernel_invocations"] is None


def test_counts_are_captured_after_each_real_lowering_pass():
    from minicompiler.passes.linear_bias_relu import run_linear_bias_relu

    a = relax.Var("a", relax.TensorType((2, 3), "float32"))
    b = relax.Var("b", relax.TensorType((3, 4), "float32"))
    bias = relax.Var("bias", relax.TensorType((4,), "float32"))
    builder = relax.BlockBuilder()
    with builder.function("main", [a, b, bias]):
        with builder.dataflow():
            mm = builder.emit(relax.op.matmul(a, b))
            add = builder.emit(relax.op.add(mm, bias))
            out = builder.emit_output(relax.op.nn.relu(add))
        builder.emit_func_output(out)
    fused, pass_report = run_linear_bias_relu(builder.get())
    assert pass_report["rewrites"] == 1
    timer = PassTimer()
    with tvm.transform.PassContext(opt_level=2, instruments=[timer]):
        legalized = relax.transform.LegalizeOps()(fused)
        relax.transform.FuseTIR()(legalized)
    counts = timer.snapshot()["static_ir_snapshots"]
    assert [(x["after_pass"], x["tir_primfunc_count"]) for x in counts] == [
        ("LegalizeOps", 3), ("FuseTIR", 1)]


def test_failed_pass_is_recorded_as_incomplete_without_invented_duration():
    import pytest

    @tvm.transform.module_pass(opt_level=0, name="InjectedFailure")
    def fail(mod, ctx):
        raise RuntimeError("injected")

    timer = PassTimer()
    with pytest.raises(Exception, match="injected"):
        with tvm.transform.PassContext(instruments=[timer]):
            fail(tvm.IRModule({}))
    result = timer.snapshot()
    assert result["incomplete_passes"] > 0
    assert "InjectedFailure" not in result["by_pass"]
