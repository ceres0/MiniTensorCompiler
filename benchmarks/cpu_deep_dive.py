"""Interleaved CPU MatMul ablation; run on native Linux with an explicit CPU set.

Example: python -m benchmarks.cpu_deep_dive --cpus 0,1 --threads 2 --output-dir runs/cpu-deep
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
from time import perf_counter_ns

STAGES = ("default", "naive", "tile", "reorder", "parallel", "vectorize")
DEFAULT_SHAPES = ((1, 128, 128), (8, 128, 128), (32, 128, 128),
                  (1, 256, 256), (8, 256, 256), (32, 256, 256))


def parse_triple(value):
    try:
        dims = tuple(int(x) for x in value.split(","))
        if len(dims) != 3 or any(x <= 0 for x in dims):
            raise ValueError()
        return dims
    except ValueError as exc:
        raise argparse.ArgumentTypeError("shape must be positive M,K,N") from exc


def parse_cpus(value):
    try:
        cpus = [int(x) for x in value.split(",")]
        if not cpus or any(x < 0 for x in cpus) or len(set(cpus)) != len(cpus):
            raise ValueError()
        return cpus
    except ValueError as exc:
        raise argparse.ArgumentTypeError("cpus must be unique nonnegative comma-separated IDs") from exc


def _assembly(executable):
    sources = []
    def visit(module):
        if module.kind == "llvm":
            try:
                source = module.inspect_source("asm")
                if source:
                    sources.append(source)
            except Exception:
                pass
        for child in module.imports:
            visit(child)
    visit(executable.mod)
    return "\n".join(sources)


def _thread_affinities():
    """Observe surviving threads; do not assume the runtime inherited affinity."""
    result = {}
    for task in Path("/proc/self/task").iterdir():
        try:
            result[task.name] = sorted(os.sched_getaffinity(int(task.name)))
        except (OSError, ProcessLookupError):
            continue  # A transient thread may have already exited.
    return result


def _violations(actual, reference, rtol, atol):
    """Summarize the allclose threshold violations without masking cancellation."""
    import numpy as np
    difference = np.abs(np.asarray(actual, dtype=np.float64) - np.asarray(reference, dtype=np.float64))
    limit = atol + rtol * np.abs(np.asarray(reference, dtype=np.float64))
    mask = difference > limit
    if not np.any(mask):
        return {"count": 0, "largest_excess": None}
    index = np.unravel_index(int(np.argmax(difference - limit)), difference.shape)
    return {"count": int(np.count_nonzero(mask)), "largest_excess": {
        "index": list(index), "actual": float(actual[index]), "reference": float(reference[index]),
        "absolute_error": float(difference[index]), "allowed_error": float(limit[index])}}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--cpus", type=parse_cpus, required=True)
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--warmup", type=int, default=30)
    p.add_argument("--repeat", type=int, default=100)
    p.add_argument("--rounds", type=int, default=5)
    p.add_argument("--rtol", type=float, default=1e-4)
    p.add_argument("--atol", type=float, default=1e-5)
    p.add_argument("--shape", type=parse_triple, action="append")
    a = p.parse_args(argv)
    if a.threads < 1 or a.threads > len(a.cpus) or a.warmup < 0 or a.repeat < 1 or a.rounds < 1 or a.seed < 0:
        p.error("threads must fit selected CPUs; seed/warmup must be nonnegative and repeat/rounds positive")
    if not math.isfinite(a.rtol) or not math.isfinite(a.atol) or a.rtol < 0 or a.atol < 0:
        p.error("rtol and atol must be finite and nonnegative")
    shapes = a.shape or DEFAULT_SHAPES
    if len(set(shapes)) != len(shapes):
        p.error("duplicate shape")
    if a.output_dir.exists():
        p.error("output directory already exists")
    if not hasattr(os, "sched_setaffinity"):
        p.error("CPU affinity requires Linux sched_setaffinity")
    available = os.sched_getaffinity(0)
    if not set(a.cpus) <= available:
        p.error(f"requested CPUs not in available set: {sorted(available)}")
    os.sched_setaffinity(0, set(a.cpus))
    for key in ("TVM_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[key] = str(a.threads)

    import numpy as np
    import tvm
    from tvm import relax
    from minicompiler.doctor import collect_report
    from minicompiler.profiling.report import _git_info
    from minicompiler.runtime.correctness import compare_outputs
    from minicompiler.schedules.matmul_cpu import make_matmul

    if tvm.runtime.num_threads() != a.threads:
        raise RuntimeError("TVM runtime thread count differs from requested")
    a.output_dir.mkdir(parents=True)
    records = []
    passed = True
    for m, k, n in shapes:
        outdir = a.output_dir / f"m{m}_k{k}_n{n}"
        outdir.mkdir()
        rng = np.random.default_rng(a.seed)
        x = rng.standard_normal((m, k), dtype=np.float32)
        w = rng.standard_normal((k, n), dtype=np.float32)
        reference = x @ w
        reference_fp64 = x.astype(np.float64) @ w.astype(np.float64)
        numpy_vs_fp64 = compare_outputs([reference], [reference_fp64], rtol=a.rtol, atol=a.atol)
        prepared = (tvm.runtime.tensor(x), tvm.runtime.tensor(w))
        stages, runners = {}, {}
        for stage in STAGES:
            try:
                bb = relax.BlockBuilder()
                av = relax.Var("a", relax.TensorType((m, k), "float32"))
                bv = relax.Var("b", relax.TensorType((k, n), "float32"))
                if stage == "default":
                    kernel = None
                else:
                    tir = make_matmul(m, k, n, stage)
                    (outdir / f"{stage}.py").write_text(tir.script() + "\n")
                    kernel = bb.add_func(tir["main"].without_attr("global_symbol"), "matmul_kernel")
                with bb.function("main", [av, bv]):
                    with bb.dataflow():
                        expr = relax.op.matmul(av, bv) if kernel is None else relax.op.call_tir(kernel, (av, bv), out_ty=relax.TensorType((m, n), "float32"))
                        output = bb.emit_output(expr)
                    bb.emit_func_output(output)
                mod = bb.get()
                if stage == "default":
                    (outdir / "default_legalized.py").write_text(relax.transform.LegalizeOps()(mod).script() + "\n")
                start = perf_counter_ns()
                with tvm.transform.PassContext(opt_level=2):
                    exe = tvm.compile(mod, target="llvm", relax_pipeline="default", tir_pipeline="default")
                elapsed = (perf_counter_ns() - start) / 1e6
                assembly = _assembly(exe)
                if assembly:
                    (outdir / f"{stage}.s").write_text(assembly)
                vm = relax.VirtualMachine(exe, tvm.cpu())
                fn = vm["main"]
                output_numpy = fn(*prepared).numpy()
                correctness = compare_outputs([output_numpy], [reference], rtol=a.rtol, atol=a.atol)
                fp64_check = compare_outputs([output_numpy], [reference_fp64], rtol=a.rtol, atol=a.atol)
                correctness["violations"] = _violations(output_numpy, reference, a.rtol, a.atol)
                fp64_check["violations"] = _violations(output_numpy, reference_fp64, a.rtol, a.atol)
                stages[stage] = {"correctness": correctness, "compile_ms": elapsed,
                                 "correctness_vs_fp64": fp64_check,
                                 "assembly_available": bool(assembly), "samples_ms": []}
                if not correctness["passed"] or not fp64_check["passed"]:
                    passed = False
                runners[stage] = (vm, fn)
            except Exception as exc:
                passed = False
                stages[stage] = {"correctness": {"passed": False}, "error": f"{type(exc).__name__}: {exc}"}
        orders = []
        if all(stages[s]["correctness"]["passed"] and stages[s]["correctness_vs_fp64"]["passed"] for s in STAGES):
            for stage in STAGES:
                for _ in range(a.warmup):
                    runners[stage][1](*prepared)
            order_rng = random.Random(a.seed + m * 100000 + k * 1000 + n)
            for _ in range(a.rounds):
                order = list(STAGES)
                order_rng.shuffle(order)
                orders.append(order)
                for stage in order:
                    fn = runners[stage][1]
                    samples = []
                    for _ in range(a.repeat):
                        start = perf_counter_ns()
                        fn(*prepared)
                        samples.append((perf_counter_ns() - start) / 1e6)
                    stages[stage]["samples_ms"].append(samples)
            for stage in STAGES:
                samples = np.asarray(stages[stage]["samples_ms"]).ravel()
                stages[stage]["median_ms"] = float(np.median(samples))
                stages[stage]["p95_ms"] = float(np.percentile(samples, 95))
            for stage in STAGES:
                stages[stage]["speedup_vs_default"] = stages["default"]["median_ms"] / stages[stage]["median_ms"]
        records.append({"shape": [m, k, n], "input_sha256": hashlib.sha256(x.tobytes() + w.tobytes()).hexdigest(),
                        "numpy_fp32_vs_fp64": numpy_vs_fp64, "stages": stages, "round_order": orders})
    environment = collect_report()
    environment.update({"affinity_requested": a.cpus, "affinity_actual": sorted(os.sched_getaffinity(0)),
                        "threads": a.threads, "tvm_runtime_threads": tvm.runtime.num_threads(),
                        "observed_thread_affinities": _thread_affinities(),
                        "target": "llvm", "power_policy": "not controlled", "background_load": "not controlled"})
    report = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), "git": _git_info(),
              "environment": environment, "seed": a.seed, "warmup": a.warmup, "repeat": a.repeat,
              "rounds": a.rounds, "rtol": a.rtol, "atol": a.atol, "results": records,
              "method": "Baseline is pinned TVM native default, not a tuned or BLAS baseline. Identical Relax VM call boundary, target and default pipeline. Shuffled stage order by round; samples include Python call and output allocation, not input preparation or NumPy conversion. Assembly from compiled LLVM modules; thread affinity is a snapshot of surviving threads, not a trace. No performance counters collected."}
    (a.output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"Report written to {a.output_dir / 'report.json'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
