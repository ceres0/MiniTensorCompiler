"""End-to-end semantics and conservative matching for the linear fusion pass."""

import numpy as np
import pytest
import tvm
from tvm import relax

from minicompiler.passes.linear_bias_relu import run_linear_bias_relu


def graph(m=3, k=5, n=4, *, dtype="float32", bias_shape=None, reverse=False,
          shared=None, constant=False, activation=True):
    bias_shape = (n,) if bias_shape is None else bias_shape
    x = relax.Var("x", relax.TensorType((m, k), dtype))
    b = relax.Var("bias", relax.TensorType(bias_shape, dtype))
    if constant:
        w = relax.const(np.arange(k*n, dtype=dtype).reshape(k,n) / 20, dtype)
        params = [x, b]
    else:
        w = relax.Var("w", relax.TensorType((k, n), dtype))
        params = [x, w, b]
    bb = relax.BlockBuilder()
    with bb.function("main", params):
        with bb.dataflow():
            mm = bb.emit(relax.op.matmul(x, w), name_hint="mm")
            add = bb.emit(relax.op.add(b, mm) if reverse else relax.op.add(mm, b), name_hint="biasadd")
            output = bb.emit(relax.op.nn.relu(add) if activation else add, name_hint="out")
            if shared:
                output = relax.Tuple([output, mm if shared == "matmul" else add])
            out = bb.emit_output(output)
        bb.emit_func_output(out)
    return bb.get()


def execute(mod, args):
    vm = relax.VirtualMachine(tvm.compile(mod, target="llvm"), tvm.cpu())
    out = vm["main"](*(tvm.runtime.tensor(x) for x in args))
    if isinstance(out, tvm.runtime.Tensor):
        return [out.numpy()]
    return [x.numpy() for x in out]


def vm_for(mod):
    return relax.VirtualMachine(tvm.compile(mod, target="llvm"), tvm.cpu())


def samples(m=3,k=5,n=4, *, seed=4, constant=False, dtype="float32", bias_shape=None):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(m,k)).astype(dtype)
    w = rng.normal(size=(k,n)).astype(dtype)
    b = rng.normal(size=bias_shape or (n,)).astype(dtype)
    return [x,b] if constant else [x,w,b]


@pytest.mark.parametrize("dims", [(1,5,4), (3,5,4), (8,8,7), (2,1,1)])
@pytest.mark.parametrize("constant", [False, True], ids=["runtime_weights", "constant_weights"])
def test_fused_graph_executes_and_matches_original_and_numpy(dims, constant):
    m,k,n = dims
    mod = graph(m,k,n,constant=constant)
    before = mod.script()
    result, report = run_linear_bias_relu(mod)
    assert report["status"] == "ok", report
    assert report["rewrites"] >= 1
    assert mod.script() == before
    assert result.script() != before
    baseline_vm, fused_vm = vm_for(mod), vm_for(result)
    for seed in (0, 17, 42):
        values = samples(m,k,n,seed=seed,constant=constant)
        tensors = [tvm.runtime.tensor(value) for value in values]
        original = baseline_vm["main"](*tensors).numpy()
        fused = fused_vm["main"](*tensors).numpy()
        w = (np.arange(k*n, dtype="float32").reshape(k,n) / 20) if constant else values[1]
        expected = np.maximum(values[0] @ w + values[-1], 0)
        np.testing.assert_allclose(original, expected, rtol=1e-4, atol=1e-5)
        np.testing.assert_allclose(fused, expected, rtol=1e-4, atol=1e-5)


@pytest.mark.parametrize("kwargs", [
    {"reverse":True},
    {"bias_shape":(3,1)},
    {"bias_shape":(1,4)},
    {"bias_shape":()},
    {"dtype":"float16"},
    {"activation":False},
])
def test_unsupported_graphs_are_unchanged(kwargs):
    mod = graph(**kwargs)
    output, report = run_linear_bias_relu(mod)
    assert report["status"] == "ok", report
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(output, mod)


@pytest.mark.parametrize("shared", ["matmul", "add"])
def test_shared_intermediate_preserves_every_consumer(shared):
    mod = graph(shared=shared)
    result, report = run_linear_bias_relu(mod)
    assert report["status"] == "ok", report
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(result, mod)
    args = samples()
    for before, after in zip(execute(mod, args), execute(result, args), strict=True):
        np.testing.assert_allclose(before, after, rtol=1e-4, atol=1e-5)


def test_disabled_and_idempotent():
    mod = graph()
    disabled, report = run_linear_bias_relu(mod, enabled=False)
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(disabled, mod)
    fused, report = run_linear_bias_relu(mod)
    assert report["rewrites"] == 1
    twice, again = run_linear_bias_relu(fused)
    assert again["rewrites"] == 0
    tvm.ir.assert_structural_equal(fused, twice)


def test_symbolic_batch_is_rejected():
    symbolic = tvm.tirx.Var("batch", "int64")
    mod = graph(m=symbolic)
    result, report = run_linear_bias_relu(mod)
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(result, mod)


def test_non_dataflow_is_safely_unchanged():
    x = relax.Var("x", relax.TensorType((3, 5), "float32"))
    w = relax.Var("w", relax.TensorType((5, 4), "float32"))
    b = relax.Var("b", relax.TensorType((4,), "float32"))
    bb = relax.BlockBuilder()
    with bb.function("main", [x, w, b]):
        mm = bb.emit(relax.op.matmul(x, w))
        add = bb.emit(relax.op.add(mm, b))
        out = bb.emit(relax.op.nn.relu(add))
        bb.emit_func_output(out)
    mod = bb.get()
    fused, report = run_linear_bias_relu(mod)
    assert report["status"] == "ok", report
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(fused, mod)
    np.testing.assert_allclose(execute(mod, samples())[0], execute(fused, samples())[0], rtol=1e-4, atol=1e-5)


def test_imported_mlp_matches_onnxruntime_after_fusion(tmp_path):
    pytest.importorskip("torch", reason="install models extra for exported MLP")
    from models.export import export_model
    from minicompiler.frontend import import_relax, load_and_summarize
    from minicompiler.runtime.correctness import make_inputs, create_ort_runner

    model_path = export_model("mlp", tmp_path / "mlp.onnx", seed=11)
    onnx_model, summary = load_and_summarize(model_path)
    mod = import_relax(onnx_model)
    fused, report = run_linear_bias_relu(mod)
    assert report["status"] == "ok", report
    assert report["rewrites"] >= 1
    inputs = make_inputs(summary, seed=29)
    expected = create_ort_runner(model_path)(inputs)
    for before, after, reference in zip(execute(mod, list(inputs.values())),
                                        execute(fused, list(inputs.values())), expected, strict=True):
        np.testing.assert_allclose(before, reference, rtol=1e-4, atol=1e-5)
        np.testing.assert_allclose(after, reference, rtol=1e-4, atol=1e-5)


def test_fused_tir_vs_separate_tir_under_same_lowering():
    original = graph()
    fused, report = run_linear_bias_relu(original)
    assert report["rewrites"] == 1
    def lower(mod):
        return relax.transform.FuseTIR()(relax.transform.LegalizeOps()(mod))
    before, after = lower(original), lower(fused)
    primfunc_count = lambda mod: sum(isinstance(f, tvm.tirx.PrimFunc) for f in mod.functions.values())
    assert primfunc_count(before) == 3
    assert primfunc_count(after) == 1
    assert "matmul_intermediate" in after.script()  # TIR still materializes intermediates
    args = samples()
    np.testing.assert_allclose(execute(before, args)[0], execute(after, args)[0], rtol=1e-4, atol=1e-5)
