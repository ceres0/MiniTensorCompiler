"""TVM 0.27 CPU baseline compilation configurations.

The TVM generic default build pipeline for this pinned version does not include
FuseOps or FuseTIR. The nofusion mode explicitly disables those passes, but
may therefore be identical to default; it is a diagnostic, not a speed baseline.
"""

import time

import tvm


def compile_module(mod, *, target="llvm", mode="default", instruments=None):
    """Compile an imported Relax module and return executable, milliseconds, metadata."""
    if mode not in ("default", "nofusion", "custom"):
        raise ValueError(f"Unsupported compilation mode: {mode}")
    target_obj = tvm.target.Target(target)
    if target_obj.kind.name != "llvm":
        raise ValueError("Only LLVM CPU targets are supported")
    disabled = ["FuseOps", "FuseTIR"] if mode == "nofusion" else []
    if mode == "custom":
        from .linear_pipeline import linear_fused_pipeline
        pipeline = linear_fused_pipeline()
    else:
        pipeline = "default"
    start = time.perf_counter_ns()
    with tvm.transform.PassContext(opt_level=2, disabled_pass=disabled, instruments=instruments or []):
        executable = tvm.compile(mod, target=target_obj, relax_pipeline=pipeline, tir_pipeline="default")
    elapsed_ms = (time.perf_counter_ns() - start) / 1e6
    metadata = {
        "mode": mode,
        "target": str(target_obj),
        "relax_pipeline": ("pinned CPU default plus FuseTIR after LegalizeOps" if mode == "custom"
                           else "tvm.compile default (generic CPU build pipeline)"),
        "tir_pipeline": "default",
        "pass_context_opt_level": 2,
        "disabled_passes": disabled,
        "note": "TVM 0.27.0.post1 CPU default has no FuseOps/FuseTIR; custom adds FuseTIR after LegalizeOps; nofusion may match default.",
    }
    return executable, elapsed_ms, metadata
