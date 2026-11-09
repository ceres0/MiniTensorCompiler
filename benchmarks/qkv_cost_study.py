"""Paired QKV packing experiment; records costs without enabling a rewrite policy.

Each round alternates order. Shape recommendations are exploratory and require
independent target-hardware validation; no result modifies the pass allowlist.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from time import perf_counter_ns


def candidate(rounds, min_speedup=1.05):
    """Require >=6 independently timed alternating rounds and no slow round.

    This conservative screen is not a statistical confidence interval and
    cannot replace a held-out measurement on the target hardware.
    """
    if len(rounds) < 6:
        return {"candidate": False, "reason": "fewer than six paired rounds"}
    if not all(r["default_median_ms"] > min_speedup * r["packed_median_ms"] for r in rounds):
        return {"candidate": False, "reason": "at least one round missed the speedup threshold"}
    return {"candidate": True, "reason": "all paired rounds exceeded threshold; independent validation required"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--shape", action="append", help="M,K,N; repeat for each shape")
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--warmup", type=int, default=30)
    p.add_argument("--repeat", type=int, default=100)
    p.add_argument("--rounds", type=int, default=6)
    args = p.parse_args(argv)
    if args.threads < 1 or args.seed < 0 or args.warmup < 0 or args.repeat < 1 or args.rounds < 1:
        p.error("threads/repeat/rounds must be positive; warmup/seed nonnegative")
    try:
        shapes = [tuple(map(int, v.split(","))) for v in (args.shape or ["1,256,256", "8,256,256", "32,256,256", "1,512,512", "8,512,512", "32,512,512"])]
        if any(len(s) != 3 or min(s) < 1 for s in shapes) or len(set(shapes)) != len(shapes):
            raise ValueError()
    except ValueError:
        p.error("shape must be unique positive M,K,N triples")
    if args.output.exists():
        p.error("output exists")
    os.environ.update(TVM_NUM_THREADS=str(args.threads), OMP_NUM_THREADS=str(args.threads), OPENBLAS_NUM_THREADS=str(args.threads))
    import numpy as np
    import tvm
    from tvm import relax
    from minicompiler.doctor import collect_report
    from minicompiler.passes.merge_qkv import run_merge_qkv
    from minicompiler.profiling.report import _git_info
    from minicompiler.runtime.correctness import compare_outputs

    if tvm.runtime.num_threads() != args.threads:
        raise RuntimeError("TVM thread count mismatch")
    environment = collect_report()
    environment.update({"threads": args.threads, "target": "llvm", "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None, "power_policy": "not controlled"})
    records = []
    all_ok = True
    for m, k, n in shapes:
        rng = np.random.default_rng(args.seed)
        weights = [rng.standard_normal((k, n), dtype=np.float32) * np.float32(.05) for _ in range(3)]
        x_data = rng.standard_normal((m, k), dtype=np.float32)
        # Isolated NumPy concat is not subtracted from Pass time (which includes more work).
        concat_times = []
        for _ in range(args.repeat):
            begin = perf_counter_ns()
            packed_weights = np.concatenate(weights, axis=1)
            concat_times.append((perf_counter_ns() - begin) / 1e6)
        x = relax.Var("x", relax.TensorType((m, k), "float32"))
        bb = relax.BlockBuilder()
        with bb.function("main", [x]):
            with bb.dataflow():
                parts = [bb.emit(relax.op.matmul(x, relax.const(w))) for w in weights]
                out = bb.emit_output(relax.Tuple(parts))
            bb.emit_func_output(out)
        original = bb.get()
        begin = perf_counter_ns()
        packed, pass_report = run_merge_qkv(original, enabled=True, allowed_shapes=[(m, k, n)])
        pass_ms = (perf_counter_ns() - begin) / 1e6
        if pass_report["status"] != "ok" or pass_report["rewrites"] != 1:
            raise RuntimeError(f"QKV rewrite failed: {pass_report}")
        # Isolated slice-only VM is a diagnostic for output splitting, not a
        # direct subtraction from fused latency (allocation/cache differ).
        combined = relax.Var("combined", relax.TensorType((m, 3*n), "float32"))
        bb = relax.BlockBuilder()
        with bb.function("main", [combined]):
            with bb.dataflow():
                slices = [bb.emit(relax.op.strided_slice(combined, axes=[1], begin=[j*n], end=[(j+1)*n])) for j in range(3)]
                out = bb.emit_output(relax.Tuple(slices))
            bb.emit_func_output(out)
        slice_mod = bb.get()
        def compile_vm(mod):
            begin = perf_counter_ns()
            with tvm.transform.PassContext(opt_level=2):
                executable = tvm.compile(mod, target="llvm", relax_pipeline="default", tir_pipeline="default")
            elapsed = (perf_counter_ns() - begin) / 1e6
            return relax.VirtualMachine(executable, tvm.cpu()), elapsed
        vms, build = {}, {}
        for name, mod in (("default", original), ("packed", packed), ("slice_only", slice_mod)):
            vms[name], build[name] = compile_vm(mod)
        device_x = tvm.runtime.tensor(x_data)
        precomputed = tvm.runtime.tensor(x_data @ packed_weights)
        calls = {"default": lambda: vms["default"]["main"](device_x), "packed": lambda: vms["packed"]["main"](device_x), "slice_only": lambda: vms["slice_only"]["main"](precomputed)}
        expected = [x_data @ w for w in weights]
        checks = {name: compare_outputs([v.numpy() for v in fn()], expected) for name, fn in calls.items()}
        ok = all(v["passed"] for v in checks.values())
        all_ok &= ok
        measurements = []
        if ok:
            for fn in calls.values():
                for _ in range(args.warmup): fn()
            for i in range(args.rounds):
                order = ["default", "packed"] if i % 2 == 0 else ["packed", "default"]
                row = {"order": order + ["slice_only"]}
                for name in row["order"]:
                    times = []
                    for _ in range(args.repeat):
                        begin = perf_counter_ns(); calls[name](); times.append((perf_counter_ns() - begin) / 1e6)
                    row[name + "_samples_ms"] = times
                    row[name + "_median_ms"] = float(np.median(times))
                measurements.append(row)
        # Upper-level tensor accounting only; allocator reuse/fusion and peak RSS
        # require profiling. Both three outputs and combined output are m*3n.
        record = {"shape": [m, k, n], "input_sha256": hashlib.sha256(x_data.tobytes()).hexdigest(),
                  "weights_sha256": hashlib.sha256(b"".join(w.tobytes() for w in weights)).hexdigest(),
                  "correctness": checks, "compile_ms": build, "pass_ms": pass_ms,
                  "numpy_concat_ms": {"median": float(np.median(concat_times)), "samples": concat_times},
                  "logical_bytes": {"three_original_weights": 12*k*n, "packed_weights": 12*k*n,
                                    "packed_intermediate": 12*m*n, "three_outputs": 12*m*n},
                  "rounds": measurements, "screen": candidate(measurements)}
        records.append(record)
    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "git": _git_info(), "environment": environment,
              "parameters": {"seed": args.seed, "threads": args.threads, "warmup": args.warmup, "repeat": args.repeat, "rounds": args.rounds},
              "method": {"pipeline": "both QKV graphs use TVM default Relax/TIR and opt_level=2",
                         "timing": "VM invocation and output allocation; precreated input; no numpy output copy; alternating paired rounds",
                         "slice_only": "standalone diagnostic, not subtractable from full packed execution",
                         "memory": "logical tensor sizes only; not measured peak or actual allocations",
                         "screen": "all >=6 paired rounds >5% improvement; exploratory, not automatic enablement; run held-out validation"},
              "results": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2, allow_nan=False); f.write("\n")
    print(f"QKV cost study written to {args.output}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
