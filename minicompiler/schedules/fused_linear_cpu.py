"""Naive static FP32 fused linear epilogue experiment, independent of graph pass."""
import tvm
from tvm.script import tirx as T


def make_fused_linear(m, k, n):
    """Return C=relu(A@W+b), with one local accumulator per output.

    This scalar-loop demonstration is not an optimized GEMM. It avoids full
    MxN temporary arrays for matmul and bias; the compiler decides whether the
    local accumulator stays in registers. Buffers must not alias.
    """
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in (m, k, n)):
        raise ValueError("M, K and N must be positive integers")

    @T.prim_func
    def fused(A: T.Buffer((m, k), "float32"), W: T.Buffer((k, n), "float32"),
              B: T.Buffer((n,), "float32"), C: T.Buffer((m, n), "float32")):
        T.func_attr({"global_symbol": "main", "tirx.noalias": True})
        for i, j in T.grid(m, n):
            acc = T.alloc_local((1,), "float32")
            acc[0] = T.float32(0)
            for r in range(k):
                acc[0] = acc[0] + A[i, r] * W[r, j]
            C[i, j] = T.max(acc[0] + B[j], T.float32(0))
    return tvm.IRModule({"main": fused})
