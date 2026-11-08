"""Semantic and structural regressions for redundant reshape elimination."""

import numpy as np
import pytest
import tvm
from tvm import relax

from minicompiler.passes.redundant_reshape import run_redundant_reshape


def make_graph(input_shape, first_shape, second_shape, *, shared=False, dtype="float32"):
    x = relax.Var("x", relax.TensorType(input_shape, dtype))
    bb = relax.BlockBuilder()
    with bb.function("main", [x]):
        with bb.dataflow():
            intermediate = bb.emit(relax.op.reshape(x, first_shape), name_hint="first")
            result = bb.emit(relax.op.reshape(intermediate, second_shape), name_hint="second")
            if shared:
                result = relax.Tuple([result, intermediate])
            out = bb.emit_output(result)
        bb.emit_func_output(out)
    return bb.get()


def count_reshape(mod):
    return mod.script().count("R.reshape(")


def evaluate(mod, x):
    executable = tvm.compile(mod, target="llvm")
    vm = relax.VirtualMachine(executable, tvm.cpu())
    result = vm["main"](tvm.runtime.tensor(x))
    if isinstance(result, tvm.runtime.Tensor):
        return [result.numpy()]
    return [value.numpy() for value in result]


@pytest.mark.parametrize("source,first,last", [
    ((2, 3), (6,), (3, 2)),
    ((2, 3), (3, 2), (6,)),
    ((1, 6), (2, 3), (1, 2, 3)),
    ((6,), (1, 2, 3), (2, 3)),
    ((2, 2, 2), (4, 2), (8,)),
    ((4, 4), (2, 8), (1, 16)),
    ((1,), (1, 1), (1,)),
    ((3, 4), (12,), (3, 4)),
])
def test_static_reshape_chains_preserve_values(source, first, last):
    mod = make_graph(source, first, last)
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] >= 1
    assert count_reshape(mod) == 2
    assert count_reshape(rewritten) == 1
    inputs = np.arange(np.prod(source), dtype=np.float32).reshape(source)
    expected = evaluate(mod, inputs)
    actual = evaluate(rewritten, inputs)
    np.testing.assert_array_equal(actual[0], expected[0])
    np.testing.assert_array_equal(actual[0], inputs.reshape(last))


def test_shared_intermediate_is_preserved_for_other_consumer():
    mod = make_graph((2, 3), (6,), (3, 2), shared=True)
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] >= 1
    assert count_reshape(rewritten) == 2
    x = np.arange(6, dtype=np.float32).reshape(2, 3)
    for before, after in zip(evaluate(mod, x), evaluate(rewritten, x), strict=True):
        np.testing.assert_array_equal(after, before)
    # The second reshape reads x, while the first remains for the other output.
    script = rewritten.script()
    assert "R.reshape(x, R.shape([3, 2]))" in script


def test_disabled_pass_keeps_original_ir():
    mod = make_graph((2, 3), (6,), (3, 2))
    result, report = run_redundant_reshape(mod, enabled=False)
    assert not report["enabled"]
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(mod, result)


def test_symbolic_shape_is_not_rewritten():
    n = tvm.tirx.Var("n", "int64")
    mod = make_graph((n, 4), (n, 2, 2), (n, 4))
    result, report = run_redundant_reshape(mod)
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(mod, result)


def test_zero_dimension_and_zero_copy_directives_are_conservatively_skipped():
    mod = make_graph((0, 3, 5), (0, 0, 5), (0, 0, 0))
    result, report = run_redundant_reshape(mod)
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(mod, result)


def test_inferred_minus_one_is_normalized_and_preserves_result():
    mod = make_graph((2, 3), (3, -1), (-1,))
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] == 1
    x = np.arange(6, dtype=np.float32).reshape(2, 3)
    np.testing.assert_array_equal(evaluate(rewritten, x)[0], evaluate(mod, x)[0])


def test_scalar_reshape_preserves_value():
    mod = make_graph((), (1,), ())
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] == 1
    x = np.asarray(3.5, dtype=np.float32)
    np.testing.assert_array_equal(evaluate(rewritten, x)[0], evaluate(mod, x)[0])


def test_integer_dtype_preserved():
    mod = make_graph((2, 3), (6,), (3, 2), dtype="int32")
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] == 1
    x = np.arange(6, dtype=np.int32).reshape(2, 3)
    np.testing.assert_array_equal(evaluate(rewritten, x)[0], evaluate(mod, x)[0])


def test_separate_reshape_branches_do_not_match():
    x = relax.Var("x", relax.TensorType((2, 3), "float32"))
    bb = relax.BlockBuilder()
    with bb.function("main", [x]):
        with bb.dataflow():
            a = bb.emit(relax.op.reshape(x, (6,)))
            b = bb.emit(relax.op.reshape(x, (3, 2)))
            output = bb.emit_output(relax.Tuple([a, b]))
        bb.emit_func_output(output)
    mod = bb.get()
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] == 0
    tvm.ir.assert_structural_equal(mod, rewritten)


def test_three_layer_chain_keeps_exact_output():
    x = relax.Var("x", relax.TensorType((2, 3), "float32"))
    bb = relax.BlockBuilder()
    with bb.function("main", [x]):
        with bb.dataflow():
            a = bb.emit(relax.op.reshape(x, (6,)))
            b = bb.emit(relax.op.reshape(a, (3, 2)))
            c = bb.emit(relax.op.reshape(b, (1, 6)))
            output = bb.emit_output(c)
        bb.emit_func_output(output)
    mod = bb.get()
    rewritten, report = run_redundant_reshape(mod)
    assert report["rewrites"] >= 1
    assert count_reshape(rewritten) < count_reshape(mod)
    values = np.arange(6, dtype=np.float32).reshape(2, 3)
    np.testing.assert_array_equal(evaluate(rewritten, values)[0], evaluate(mod, values)[0])


def test_incompatible_static_shapes_are_rejected_by_tvm():
    # Invalid Relax graphs cannot reach the pass through a normalized builder.
    with pytest.raises(ValueError, match="convertible"):
        make_graph((2, 3), (5,), (5,))


def test_report_and_idempotence_preserve_original_module():
    original = make_graph((2, 3), (6,), (3, 2))
    original_script = original.script()
    first, report = run_redundant_reshape(original)
    assert original.script() == original_script
    assert report["matches"] == report["rewrites"] == 1
    assert report["skipped"] == 0
    assert report["events"][0]["action"] == "rewritten"
    assert report["events"][0]["input_shape"] == [2, 3]
    second, second_report = run_redundant_reshape(first)
    assert second_report["rewrites"] == 0
    tvm.ir.assert_structural_equal(first, second)


def test_dynamic_skip_is_reported():
    n = tvm.tirx.Var("n", "int64")
    mod = make_graph((n, 4), (n, 2, 2), (n, 4))
    _, report = run_redundant_reshape(mod)
    assert report["matches"] == report["skipped"] >= 1
    assert any("symbolic" in event["reason"] for event in report["events"])
