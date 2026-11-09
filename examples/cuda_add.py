"""Compile and execute a small TVM Relax/call_tir CUDA kernel.

Run on a Linux host with an accessible NVIDIA GPU, compatible driver,
NVIDIA Container Toolkit and a CUDA-enabled TVM wheel/toolchain. This is a
GPU smoke test, not a benchmark or a claim that the model CLI targets CUDA.
"""

import sys

import numpy as np
import tvm
from tvm import relax
from tvm.script import relax as R
from tvm.script import tirx as T


@tvm.script.ir_module
class CudaAdd:
    @T.prim_func(s_tir=True)
    def add(a: T.Buffer((128,), "float32"), b: T.Buffer((128,), "float32"), out: T.Buffer((128,), "float32")):
        T.func_attr({"tirx.noalias": True})
        for block in T.thread_binding(4, thread="blockIdx.x"):
            for lane in T.thread_binding(32, thread="threadIdx.x"):
                with T.sblock("add"):
                    i = T.axis.spatial(128, block * 32 + lane)
                    out[i] = a[i] + b[i]

    @R.function
    def main(a: R.Tensor((128,), "float32"), b: R.Tensor((128,), "float32")) -> R.Tensor((128,), "float32"):
        return R.call_tir(CudaAdd.add, (a, b), out_ty=R.Tensor((128,), "float32"))


def main():
    if not tvm.runtime.enabled("cuda"):
        print("CUDA unavailable: TVM CUDA runtime is not enabled", file=sys.stderr)
        return 1
    device = tvm.cuda(0)
    if not device.exist:
        print("CUDA unavailable: no accessible NVIDIA CUDA device", file=sys.stderr)
        return 1
    a = np.arange(128, dtype="float32")
    b = np.linspace(-2, 2, 128, dtype="float32")
    try:
        executable = tvm.compile(CudaAdd, target="cuda")
        vm = relax.VirtualMachine(executable, device)
        result = vm["main"](tvm.runtime.tensor(a, device=device), tvm.runtime.tensor(b, device=device))
        device.sync()
        np.testing.assert_allclose(result.numpy(), a + b, rtol=1e-6, atol=1e-6)
    except Exception as exc:
        print(f"CUDA compilation or execution failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print("TVM CUDA Relax/call_tir Add compiled and passed on GPU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
