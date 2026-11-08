"""Relax invokes a destination-passing TensorIR kernel on the LLVM CPU."""

import numpy as np
import tvm
from tvm import relax
from tvm.script import relax as R
from tvm.script import tirx as T


@tvm.script.ir_module
class CallTIRModule:
    @T.prim_func(s_tir=True)
    def add_one(a: T.Buffer((4,), "float32"), out: T.Buffer((4,), "float32")):
        T.func_attr({"tirx.noalias": True})
        for i in T.serial(4):
            with T.sblock("add_one"):
                vi = T.axis.spatial(4, i)
                out[vi] = a[vi] + T.float32(1)

    @R.function
    def main(x: R.Tensor((4,), "float32")) -> R.Tensor((4,), "float32"):
        y = R.call_tir(CallTIRModule.add_one, (x,), out_ty=R.Tensor((4,), "float32"))
        return y


def main():
    print("=== Relax and TensorIR ===")
    print(CallTIRModule.script())
    executable = tvm.compile(CallTIRModule, target="llvm")
    print("=== VM executable ===")
    print(executable.as_text())
    vm = relax.VirtualMachine(executable, tvm.cpu())
    x = np.arange(4, dtype="float32")
    actual = vm["main"](tvm.runtime.tensor(x)).numpy()
    np.testing.assert_allclose(actual, x + 1)
    print("call_tir output:", actual)


if __name__ == "__main__":
    main()
