"""CPU MatMul schedule ablation against TVM's default Relax pipeline.

Example: python -m benchmarks.matmul_schedule --output-dir runs/matmul-ablation
Both the baseline and each scheduled kernel execute through Relax VM using
prepared CPU tensors. Each invocation includes runtime output allocation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from time import perf_counter_ns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--repeat", type=int, default=100)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--shape", action="append", help="M,K,N; repeat to override the default matrix")
    args = parser.parse_args()
    if args.threads < 1 or args.seed < 0 or args.warmup < 0 or args.repeat < 1 or args.rounds < 1:
        parser.error("threads, repeat, rounds must be positive; seed and warmup must be nonnegative")
    shapes = [(1, 128, 128), (8, 128, 128), (32, 128, 128),
              (1, 256, 256), (8, 256, 256), (32, 256, 256)]
    if args.shape:
        try:
            shapes = [tuple(int(x) for x in shape.split(",")) for shape in args.shape]
            if any(len(shape) != 3 or min(shape) <= 0 for shape in shapes) or len(set(shapes)) != len(shapes):
                raise ValueError()
        except ValueError:
            parser.error("--shape must be unique positive M,K,N triples")
    if args.output_dir.exists():
        parser.error("output directory exists; choose a new directory")
    os.environ["TVM_NUM_THREADS"] = str(args.threads)
    os.environ["OMP_NUM_THREADS"] = str(args.threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(args.threads)

    import numpy as np
    import tvm
    from tvm import relax
    from minicompiler.doctor import collect_report
    from minicompiler.profiling.benchmark import measure
    from minicompiler.profiling.report import _git_info
    from minicompiler.runtime.correctness import compare_outputs
    from minicompiler.schedules.matmul_cpu import make_matmul

    if tvm.runtime.num_threads() != args.threads:
        raise RuntimeError("TVM thread count does not match requested value")
    environment = collect_report()
    environment.update({"requested_threads": args.threads, "tvm_runtime_threads": tvm.runtime.num_threads(),
                        "target": "llvm", "cpu_affinity": "not controlled", "power_policy": "not controlled"})
    args.output_dir.mkdir(parents=True)
    records = []
    all_ok = True
    for m, k, n in shapes:
        shape_dir = args.output_dir / f"m{m}_k{k}_n{n}"
        shape_dir.mkdir()
        rng = np.random.default_rng(args.seed)
        a = rng.standard_normal((m, k), dtype=np.float32)
        b = rng.standard_normal((k, n), dtype=np.float32)
        expected = a @ b
        prepared = (tvm.runtime.tensor(a), tvm.runtime.tensor(b))
        stages = {}
        for stage in ("default", "naive", "tile", "reorder", "parallel", "vectorize"):
            try:
                if stage == "default":
                    builder = relax.BlockBuilder()
                    x = relax.Var("a", relax.TensorType((m, k), "float32"))
                    y = relax.Var("b", relax.TensorType((k, n), "float32"))
                    with builder.function("main", [x, y]):
                        with builder.dataflow():
                            out = builder.emit_output(relax.op.matmul(x, y))
                        builder.emit_func_output(out)
                    mod = builder.get()
                    (shape_dir / "default_relax.py").write_text(mod.script() + "\n", encoding="utf-8")
                    inspection = relax.transform.LegalizeOps()(mod)
                    (shape_dir / "default_tir.py").write_text(inspection.script() + "\n", encoding="utf-8")
                else:
                    scheduled = make_matmul(m, k, n, stage)
                    (shape_dir / f"{stage}_tir.py").write_text(scheduled.script() + "\n", encoding="utf-8")
                    primfuncs = [func for func in scheduled.functions.values() if isinstance(func, tvm.tirx.PrimFunc)]
                    if len(primfuncs) != 1:
                        raise ValueError(f"expected one scheduled PrimFunc in {stage}, found {len(primfuncs)}")
                    builder = relax.BlockBuilder()
                    # The source PrimFunc exports "main" for standalone use; clear
                    # that symbol before placing it alongside Relax's own main.
                    kernel = builder.add_func(primfuncs[0].without_attr("global_symbol"), "matmul_kernel")
                    x = relax.Var("a", relax.TensorType((m, k), "float32"))
                    y = relax.Var("b", relax.TensorType((k, n), "float32"))
                    with builder.function("main", [x, y]):
                        with builder.dataflow():
                            out = builder.emit_output(relax.op.call_tir(kernel, (x, y), out_ty=relax.TensorType((m, n), "float32")))
                        builder.emit_func_output(out)
                    mod = builder.get()
                start = perf_counter_ns()
                with tvm.transform.PassContext(opt_level=2):
                    executable = tvm.compile(mod, target="llvm", relax_pipeline="default", tir_pipeline="default")
                compile_ms = (perf_counter_ns() - start) / 1e6
                vm = relax.VirtualMachine(executable, tvm.cpu())
                run = vm["main"]
                correctness = compare_outputs([run(*prepared).numpy()], [expected])
                entry = {"correctness": correctness, "compile_ms": compile_ms}
                if correctness["passed"]:
                    entry["inference"] = measure(lambda: run(*prepared), args.warmup, args.repeat, args.rounds)
                else:
                    all_ok = False
            except Exception as exc:
                all_ok = False
                entry = {"correctness": {"passed": False}, "error": f"{type(exc).__name__}: {exc}"}
            stages[stage] = entry
        if all(entry["correctness"]["passed"] for entry in stages.values()):
            base = stages["default"]["inference"]["median_ms"]
            for entry in stages.values():
                entry["speedup_vs_tvm_default"] = base / entry["inference"]["median_ms"]
        records.append({"shape": {"M": m, "K": k, "N": n},
                        "input_sha256": hashlib.sha256(a.tobytes() + b.tobytes()).hexdigest(), "stages": stages})
    report = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), "git": _git_info(),
              "environment": environment, "seed": args.seed, "results": records,
              "method": {"baseline": "Relax matmul compiled with TVM default Relax and TIR pipelines",
                         "scheduled": "handwritten TIR wrapped in Relax call_tir and compiled with the same default pipelines",
                         "scope": "Relax VM Python function invocation, prepared CPU tensors and runtime output allocation; no explicit output numpy copy",
                         "ordering": "default then each stage in fixed order, sequentially; not interleaved",
                         "warnings": "CPU affinity, power policy and background load not controlled; a single run is not proof of speedup"}}
    (args.output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"MatMul ablation report written to {args.output_dir / 'report.json'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
