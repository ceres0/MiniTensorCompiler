"""Show guarded linear fusion, structural TIR evidence, and CPU correctness."""

import argparse
import json
from pathlib import Path

import numpy as np
import tvm
from tvm import relax
from tvm.script import relax as R

from minicompiler.compiler.linear_pipeline import linear_fused_pipeline
from minicompiler.passes.linear_bias_relu import run_linear_bias_relu


@tvm.script.ir_module
class Linear:
    @R.function
    def main(x: R.Tensor((2, 4), "float32"), w: R.Tensor((4, 3), "float32"),
             bias: R.Tensor((3,), "float32")) -> R.Tensor((2, 3), "float32"):
        with R.dataflow():
            product = R.matmul(x, w)
            biased = R.add(product, bias)
            activated = R.nn.relu(biased)
            R.output(activated)
        return activated


def primfunc_count(mod):
    return sum(isinstance(func, tvm.tirx.PrimFunc) for func in mod.functions.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    names = ("00_relax_before.py", "01_relax_after.py", "02_tir_before.py", "03_tir_after.py", "04_report.json")
    if args.output_dir and any((args.output_dir / name).exists() for name in names):
        parser.error("output files already exist; choose a new directory")

    before = Linear
    after, report = run_linear_bias_relu(before)
    if report["status"] != "ok" or report["rewrites"] != 1:
        raise RuntimeError(f"expected one fusion: {report}")
    # These explicit transformations are separate inspection artifacts only;
    # compilation below starts from the original high-level modules.
    tir_before = relax.transform.FuseTIR()(relax.transform.LegalizeOps()(before))
    tir_after = relax.transform.FuseTIR()(relax.transform.LegalizeOps()(after))
    assert primfunc_count(tir_before) == 3 and primfunc_count(tir_after) == 1

    rng = np.random.default_rng(17)
    inputs = [rng.standard_normal(shape, dtype=np.float32) for shape in ((2, 4), (4, 3), (3,))]
    expected = np.maximum(inputs[0] @ inputs[1] + inputs[2], 0)
    outputs = []
    for module, pipeline in ((before, "default"), (after, linear_fused_pipeline())):
        exe = tvm.compile(module, target="llvm", relax_pipeline=pipeline)
        vm = relax.VirtualMachine(exe, tvm.cpu())
        outputs.append(vm["main"](*[tvm.runtime.tensor(x) for x in inputs]).numpy())
    for result in outputs:
        np.testing.assert_allclose(result, expected, rtol=1e-4, atol=1e-5)
    report["inspection"] = {"unfused_tir_primfunc_count": primfunc_count(tir_before),
                            "fused_tir_primfunc_count": primfunc_count(tir_after),
                            "runtime_kernel_invocations": None,
                            "note": "Static IR counts only. Fused TIR still contains intermediate buffers."}
    report["max_abs_error"] = float(np.max(np.abs(outputs[0] - outputs[1])))
    print(json.dumps(report, indent=2))
    print("LLVM VM baseline and fused outputs match NumPy")
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, mod in zip(names[:4], (before, after, tir_before, tir_after), strict=True):
            (args.output_dir / name).write_text(mod.script() + "\n", encoding="utf-8")
        (args.output_dir / names[4]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
