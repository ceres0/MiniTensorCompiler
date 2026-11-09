"""Test full-output semantics and the authored fused epilogue."""
import json
import os
import subprocess
import sys

import numpy as np
import pytest
import tvm
from minicompiler.schedules.fused_linear_cpu import make_fused_linear


@pytest.mark.parametrize('m,k,n', [(1,1,1), (2,3,4), (5,17,7), (8,32,19), (1,128,64)])
@pytest.mark.parametrize('seed', [0, 11])
def test_fused_kernel_against_numpy(m,k,n,seed):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((m,k),dtype=np.float32)
    w = rng.standard_normal((k,n),dtype=np.float32)
    bias = rng.standard_normal(n,dtype=np.float32)
    expected = np.maximum(x @ w + bias, 0)
    fn = tvm.compile(make_fused_linear(m,k,n),target='llvm')['main']
    out = tvm.runtime.tensor(np.full((m,n), -99, dtype=np.float32))
    for _ in range(2):
        fn(tvm.runtime.tensor(x),tvm.runtime.tensor(w),tvm.runtime.tensor(bias),out)
        np.testing.assert_allclose(out.numpy(),expected,rtol=1e-4,atol=1e-5)


def test_no_full_intermediate_buffer_in_authored_tir():
    text = make_fused_linear(2,3,4).script()
    assert 'C[i, j] = T.max(' in text
    assert 'T.alloc_buffer' not in text
    assert 'acc: T.float32' in text


@pytest.mark.parametrize('shape', [(0,2,3), (True,2,3), (1,2,-1)])
def test_invalid_dimensions(shape):
    with pytest.raises(ValueError): make_fused_linear(*shape)


def test_benchmark_with_real_graph_path(tmp_path):
    out = tmp_path / 'linear'
    env = dict(os.environ, TVM_NUM_THREADS='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    run = subprocess.run([sys.executable,'-m','benchmarks.fused_linear','--output-dir',str(out),
                          '--shape','2,3,4','--warmup','0','--repeat','2','--rounds','1'],
                         capture_output=True,text=True,env=env)
    assert run.returncode == 0, run.stderr
    record = json.loads((out / 'report.json').read_text())['results'][0]
    assert all(x['correctness']['passed'] for x in record['stages'].values())
    assert record['graph_over_scalar_speedup'] > 0
    assert (out / 'm2_k3_n4' / 'graph_fused_tir.py').exists()
    assert (out / 'm2_k3_n4' / 'scalar_fused_tir.py').exists()
