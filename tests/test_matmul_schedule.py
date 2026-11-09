"""Numerical and structural tests for the progressive CPU schedules."""

import os
import subprocess
import sys

import numpy as np
import pytest
import tvm
from tvm import relax

from minicompiler.schedules.matmul_cpu import STAGES, make_matmul


def _default_relax(m, k, n):
    a = relax.Var("a", relax.TensorType((m, k), "float32"))
    b = relax.Var("b", relax.TensorType((k, n), "float32"))
    builder = relax.BlockBuilder()
    with builder.function("main", [a, b]):
        with builder.dataflow():
            out = builder.emit_output(relax.op.matmul(a, b))
        builder.emit_func_output(out)
    return tvm.compile(builder.get(), target="llvm", relax_pipeline="default")


@pytest.mark.parametrize("m,k,n", [(1, 1, 1), (1, 7, 3), (5, 7, 11), (9, 17, 35), (16, 16, 32), (3, 33, 5)])
def test_schedules_match_numpy_and_tvm_default(m, k, n):
    rng = np.random.default_rng(m * 10000 + k * 100 + n)
    a = rng.uniform(-1, 1, (m, k)).astype("float32")
    b = rng.uniform(-1, 1, (k, n)).astype("float32")
    dev_a, dev_b = tvm.runtime.tensor(a), tvm.runtime.tensor(b)
    default = relax.VirtualMachine(_default_relax(m, k, n), tvm.cpu())
    expected = a @ b
    baseline = default["main"](dev_a, dev_b).numpy()
    np.testing.assert_allclose(baseline, expected, rtol=1e-4, atol=1e-5)
    for stage in STAGES:
        kernel = tvm.compile(make_matmul(m, k, n, stage), target="llvm")
        # A nonzero initial output and a second invocation catch a missing reset.
        out = tvm.runtime.tensor(np.full((m, n), 17, dtype="float32"))
        for _ in range(2):
            kernel["main"](dev_a, dev_b, out)
            np.testing.assert_allclose(out.numpy(), expected, rtol=1e-4, atol=1e-5, err_msg=stage)
            np.testing.assert_allclose(out.numpy(), baseline, rtol=1e-4, atol=1e-5, err_msg=stage)


@pytest.mark.parametrize("m,k,n", [(0, 2, 3), (-1, 2, 3), (1, 0, 3), (1, 2, -1), (True, 2, 3), (1.5, 2, 3)])
def test_invalid_shapes_are_rejected(m, k, n):
    with pytest.raises((ValueError, TypeError)):
        make_matmul(m, k, n, "naive")


def test_invalid_schedule_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        make_matmul(3, 4, 5, "invalid")


def test_parallel_and_vectorization_appear_only_in_expected_stages():
    scripts = {stage: make_matmul(17, 19, 35, stage).script() for stage in STAGES}
    assert all("T.parallel(" not in scripts[stage] for stage in ("naive", "tile", "reorder"))
    assert "T.parallel(" in scripts["parallel"] and "T.parallel(" in scripts["vectorize"]
    assert all("T.vectorized(" not in scripts[stage] for stage in STAGES[:-1])
    assert "T.vectorized(" in scripts["vectorize"]
    assert scripts["tile"] != scripts["reorder"]


@pytest.mark.parametrize("stage", ["parallel", "vectorize"])
def test_parallel_execution_with_two_tvm_threads(stage):
    code = '''
import numpy as np
import tvm
from minicompiler.schedules.matmul_cpu import make_matmul
assert tvm.runtime.num_threads() == 2
rng = np.random.default_rng(22)
a = rng.uniform(-1,1,(19,13)).astype("float32")
b = rng.uniform(-1,1,(13,35)).astype("float32")
f = tvm.compile(make_matmul(19,13,35,STAGE),target="llvm")
x,y = tvm.runtime.tensor(a),tvm.runtime.tensor(b)
out = tvm.runtime.tensor(np.full((19,35),5,dtype="float32"))
for _ in range(5):
    f["main"](x,y,out)
    np.testing.assert_allclose(out.numpy(), a @ b, rtol=1e-4, atol=1e-5)
'''.replace("STAGE", repr(stage))
    env = os.environ.copy()
    env.update(TVM_NUM_THREADS="2", OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="1")
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
