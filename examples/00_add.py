"""Compile, run, export and reload a minimal Relax Add on the LLVM CPU.

The compiler, runtime and generated native code are provided by Apache TVM.
"""

from pathlib import Path
import tempfile

import numpy as np
import tvm
from tvm import relax
from tvm.script import relax as R


@tvm.script.ir_module
class AddModule:
    @R.function
    def main(x: R.Tensor((3, 4), "float32"), y: R.Tensor((3, 4), "float32")):
        return R.add(x, y)


def main() -> None:
    x = np.arange(12, dtype="float32").reshape(3, 4)
    y = np.full((3, 4), 2, dtype="float32")
    expected = x + y
    executable = tvm.compile(AddModule, target="llvm")

    def check(module):
        vm = relax.VirtualMachine(module, tvm.cpu())
        result = vm["main"](tvm.runtime.tensor(x), tvm.runtime.tensor(y))
        actual = result.numpy()
        np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-6)
        return actual

    check(executable)
    with tempfile.TemporaryDirectory(prefix="minicompiler-add-") as tmp:
        library = Path(tmp) / "add.so"
        executable.export_library(str(library))
        actual = check(tvm.runtime.load_module(str(library)))
    print("Relax Add: LLVM compile, VM execution and export/reload passed")
    print(actual)


if __name__ == "__main__":
    main()
