"""Sequential experimental QKV shape matrix against the same TVM default pipeline.

Example: python -m benchmarks.qkv_matrix --threads 1 --output runs/qkv-matrix.json
Shapes are explicitly allowlisted for measurement only. Results do not alter the
pass's disabled-by-default policy and do not automatically select profitable shapes.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--repeat", type=int, default=100)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.threads < 1 or args.seed < 0 or args.warmup < 0 or args.repeat < 1 or args.rounds < 1:
        parser.error("threads, repeat and rounds must be positive; seed and warmup must be nonnegative")
    if args.output.exists():
        parser.error("output exists; choose a new path")
    os.environ["TVM_NUM_THREADS"] = str(args.threads)
    os.environ["OMP_NUM_THREADS"] = str(args.threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(args.threads)

    import numpy as np
    import tvm
    from tvm import relax
    from minicompiler.doctor import collect_report
    from minicompiler.passes.merge_qkv import run_merge_qkv
    from minicompiler.profiling.benchmark import measure
    from minicompiler.profiling.report import _git_info
    from minicompiler.runtime.correctness import compare_outputs

    if tvm.runtime.num_threads() != args.threads:
        raise RuntimeError("TVM thread count did not match the requested setting")
    environment = collect_report()
    environment.update({"requested_threads": args.threads, "tvm_runtime_threads": tvm.runtime.num_threads(),
                        "target": "llvm", "cpu_affinity": "not controlled", "power_policy": "not controlled"})
    records = []
    for size in (256, 512):
        for batch in (1, 8, 32):
            rng = np.random.default_rng(args.seed)
            weights = [rng.standard_normal((size, size), dtype=np.float32) * np.float32(0.05) for _ in range(3)]
            inputs = rng.standard_normal((batch, size), dtype=np.float32)
            x = relax.Var("x", relax.TensorType((batch, size), "float32"))
            builder = relax.BlockBuilder()
            with builder.function("main", [x]):
                with builder.dataflow():
                    projections = [builder.emit(relax.op.matmul(x, relax.const(w))) for w in weights]
                    result = builder.emit_output(relax.Tuple(projections))
                builder.emit_func_output(result)
            baseline = builder.get()
            start = perf_counter_ns()
            combined, pass_report = run_merge_qkv(baseline, enabled=True, allowed_shapes=[(batch, size, size)])
            pass_ms = (perf_counter_ns() - start) / 1e6
            if pass_report["status"] != "ok" or pass_report["rewrites"] != 1:
                raise RuntimeError(f"QKV rewrite failed: {pass_report}")
            def build(mod):
                start = perf_counter_ns()
                with tvm.transform.PassContext(opt_level=2):
                    executable = tvm.compile(mod, target="llvm", relax_pipeline="default", tir_pipeline="default")
                elapsed = (perf_counter_ns() - start) / 1e6
                vm = relax.VirtualMachine(executable, tvm.cpu())
                return vm, elapsed
            default_vm, default_ms = build(baseline)
            packed_vm, packed_ms = build(combined)
            tensor = tvm.runtime.tensor(inputs)
            reference = [x.numpy() for x in default_vm["main"](tensor)]
            actual = [x.numpy() for x in packed_vm["main"](tensor)]
            correctness = compare_outputs(actual, reference)
            record = {"shape": {"M": batch, "K": size, "N": size},
                      "input_sha256": hashlib.sha256(inputs.tobytes()).hexdigest(),
                      "weights_sha256": hashlib.sha256(b"".join(w.tobytes() for w in weights)).hexdigest(),
                      "correctness": correctness, "pass": pass_report,
                      "compilation_ms": {"default": default_ms, "custom": packed_ms, "custom_pass": pass_ms}}
            if not correctness["passed"]:
                records.append(record)
                break
            default_time = measure(lambda: default_vm["main"](tensor), args.warmup, args.repeat, args.rounds)
            packed_time = measure(lambda: packed_vm["main"](tensor), args.warmup, args.repeat, args.rounds)
            record["inference"] = {"default": default_time, "custom": packed_time,
                                   "speedup_default_over_custom": default_time["median_ms"] / packed_time["median_ms"]}
            records.append(record)
        if not records[-1]["correctness"]["passed"]:
            break
    report = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), "git": _git_info(),
              "environment": environment, "seed": args.seed, "results": records,
              "method": {"scope": "CPU Python VM invocation with pre-created input and runtime output allocation; no NumPy output copy",
                         "compile": "both paths use identical tvm.compile default Relax/TIR pipeline and opt_level=2; custom adds an explicitly enabled QKV pass before compilation",
                         "ordering": "default measured then custom, sequentially; not interleaved",
                         "allowlist": "each shape is allowed only for this experiment; no production auto-selection",
                         "warnings": "CPU affinity, power policy and background load not controlled; one run is not proof of speedup"}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"QKV matrix report written to {args.output}")
    return 0 if len(records) == 6 and all(r["correctness"]["passed"] for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
