"""Run a guarded reshape rewrite and compare LLVM VM outputs before and after."""

import argparse
import json
from pathlib import Path

import numpy as np
import tvm
from tvm import relax
from tvm.script import relax as R

from minicompiler.passes.redundant_reshape import run_redundant_reshape


@tvm.script.ir_module
class ReshapeChain:
    @R.function
    def main(x: R.Tensor((2, 3), "float32")) -> R.Tensor((6,), "float32"):
        with R.dataflow():
            intermediate = R.reshape(x, R.shape([3, 2]))
            result = R.reshape(intermediate, R.shape([6]))
            R.output(result)
        return result


def execute(module, inputs):
    executable = tvm.compile(module, target="llvm")
    vm = relax.VirtualMachine(executable, tvm.cpu())
    return vm["main"](tvm.runtime.tensor(inputs)).numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="optional directory for IR and rewrite report")
    args = parser.parse_args()
    if args.output_dir and any((args.output_dir / name).exists() for name in (
        "before.py", "after.py", "report.json"
    )):
        parser.error("output files already exist; choose a new directory")
    before = ReshapeChain
    after, report = run_redundant_reshape(before)
    x = np.arange(6, dtype="float32").reshape(2, 3)
    result_before, result_after = execute(before, x), execute(after, x)
    np.testing.assert_array_equal(result_before, x.reshape(6))
    np.testing.assert_array_equal(result_after, result_before)
    before_ir, after_ir = before.script(), after.script()
    print("=== Before ===")
    print(before_ir)
    print("=== After ===")
    print(after_ir)
    print("=== Rewrite report ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("LLVM VM outputs match:", result_after)
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "before.py").write_text(before_ir + "\n", encoding="utf-8")
        (args.output_dir / "after.py").write_text(after_ir + "\n", encoding="utf-8")
        (args.output_dir / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
