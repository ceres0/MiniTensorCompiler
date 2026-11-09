"""A progressive set of CPU TensorIR schedules for static FP32 matmul."""

import tvm
from tvm.script import tirx as T

STAGES = ("naive", "tile", "reorder", "parallel", "vectorize")


def make_matmul(m: int, k: int, n: int, stage: str = "naive"):
    """Return a TIRx IRModule for C[M,N] = A[M,K] @ B[K,N].

    The fixed tile factors are demonstration parameters, not autotuning. Split
    predicates preserve correctness when dimensions are not divisible by tiles.
    """
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in (m, k, n)):
        raise ValueError("M, K, and N must be positive integers")
    if stage not in STAGES:
        raise ValueError(f"unknown schedule stage: {stage}")

    @T.prim_func(s_tir=True)
    def matmul(A: T.Buffer((m, k), "float32"), B: T.Buffer((k, n), "float32"), C: T.Buffer((m, n), "float32")):
        T.func_attr({"global_symbol": "main", "tirx.noalias": True})
        for i, j, r in T.grid(m, n, k):
            with T.sblock("matmul"):
                vi, vj, vr = T.axis.remap("SSR", [i, j, r])
                with T.init():
                    C[vi, vj] = T.float32(0)
                C[vi, vj] = C[vi, vj] + A[vi, vr] * B[vr, vj]

    mod = tvm.IRModule({"main": matmul})
    if stage == "naive":
        return mod
    sch = tvm.s_tir.Schedule(mod)
    block = sch.get_sblock("matmul")
    i, j, r = sch.get_loops(block)
    io, ii = sch.split(i, factors=[None, 8])
    jo, ji = sch.split(j, factors=[None, 32])
    ro, ri = sch.split(r, factors=[None, 8])
    if stage in ("reorder", "parallel", "vectorize"):
        sch.reorder(io, jo, ro, ii, ri, ji)
    if stage in ("parallel", "vectorize"):
        sch.parallel(io)
    if stage == "vectorize":
        jouter, jinner = sch.split(ji, factors=[None, 4])
        sch.vectorize(jinner)
    return sch.mod
