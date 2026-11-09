"""Conservative output-parallel CUDA MatMul schedule (not shared-memory tiled)."""

import tvm
from minicompiler.schedules.matmul_cpu import make_matmul


def make_cuda_matmul(m, k, n, threads=128):
    """Map one output row to blockIdx.y, column tiles to blockIdx.x, N to threads.

    K remains serial per output, so no cross-thread reduction/synchronization is
    required. Bounds are guarded by TVM's split predicate for non-divisible N.
    """
    if not isinstance(threads, int) or isinstance(threads, bool) or not 1 <= threads <= 1024:
        raise ValueError("threads must be an integer in [1, 1024]")
    sch = tvm.s_tir.Schedule(make_matmul(m, k, n))
    block = sch.get_sblock("matmul")
    i, j, _ = sch.get_loops(block)
    jo, ji = sch.split(j, factors=[None, threads])
    sch.bind(i, "blockIdx.y")
    sch.bind(jo, "blockIdx.x")
    sch.bind(ji, "threadIdx.x")
    return sch.mod
