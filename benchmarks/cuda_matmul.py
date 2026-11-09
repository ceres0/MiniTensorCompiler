"""Compare a manually mapped CUDA MatMul to TVM's target-specific GPU default.

Run on a CUDA host with: python -m benchmarks.cuda_matmul --output-dir runs/cuda-matmul
Both versions use Relax VM and synchronize after each invocation. This is not
an optimized shared-memory kernel; it exposes a simple, measurable baseline.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from time import perf_counter_ns


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--repeat", type=int, default=100)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--shape", action="append", help="M,K,N; repeat for multiple shapes")
    args = parser.parse_args(argv)
    if args.warmup < 0 or args.repeat < 1 or args.rounds < 1 or args.seed < 0:
        parser.error("invalid iteration count or seed")
    try:
        shapes = [tuple(map(int, x.split(","))) for x in args.shape] if args.shape else [(1,128,128),(32,128,128),(32,256,256),(17,65,70)]
        if any(len(s) != 3 or min(s) < 1 for s in shapes) or len(set(shapes)) != len(shapes):
            raise ValueError()
    except ValueError:
        parser.error("shape must be unique positive M,K,N triples")
    if args.output_dir.exists():
        parser.error("output directory exists")
    import numpy as np
    import tvm
    from tvm import relax
    from minicompiler.schedules.matmul_cuda import make_cuda_matmul
    from minicompiler.runtime.correctness import compare_outputs
    from minicompiler.profiling.report import _git_info
    from minicompiler.doctor import collect_report
    try:
        if not tvm.runtime.enabled("cuda") or not tvm.cuda(0).exist:
            raise RuntimeError("CUDA runtime or device unavailable")
        dev = tvm.cuda(0)
        target = tvm.target.Target("cuda")
        pipeline = relax.get_default_pipeline(target)
    except Exception as exc:
        print(f"CUDA unavailable: {exc}")
        return 1
    args.output_dir.mkdir(parents=True)
    records = []
    success = True
    for m, k, n in shapes:
        rng = np.random.default_rng(args.seed)
        a = rng.standard_normal((m,k), dtype=np.float32)
        b = rng.standard_normal((k,n), dtype=np.float32)
        expected = a @ b
        gpu_a, gpu_b = tvm.runtime.tensor(a, device=dev), tvm.runtime.tensor(b, device=dev)
        shape_dir = args.output_dir / f"m{m}_k{k}_n{n}"
        shape_dir.mkdir()
        entries, funcs = {}, {}
        for name in ("default", "mapped"):
            try:
                builder = relax.BlockBuilder()
                x = relax.Var("a", relax.TensorType((m,k), "float32"))
                y = relax.Var("b", relax.TensorType((k,n), "float32"))
                if name == "mapped":
                    kernel = make_cuda_matmul(m,k,n)
                    (shape_dir / "mapped_tir.py").write_text(kernel.script()+"\n")
                    gv = builder.add_func(kernel["main"].without_attr("global_symbol"), "mapped_matmul")
                with builder.function("main", [x,y]):
                    with builder.dataflow():
                        expr = relax.op.matmul(x,y) if name == "default" else relax.op.call_tir(gv,(x,y),out_ty=relax.TensorType((m,n),"float32"))
                        out = builder.emit_output(expr)
                    builder.emit_func_output(out)
                mod = builder.get()
                (shape_dir / f"{name}_input.py").write_text(mod.script()+"\n")
                start = perf_counter_ns()
                with tvm.transform.PassContext(opt_level=2):
                    exe = tvm.compile(mod, target=target, relax_pipeline=pipeline)
                compile_ms = (perf_counter_ns()-start)/1e6
                vm = relax.VirtualMachine(exe, dev)
                fn = vm["main"]
                result = fn(gpu_a,gpu_b)
                dev.sync()
                check = compare_outputs([result.numpy()], [expected])
                entries[name] = {"compile_ms":compile_ms,"correctness":check}
                if check["passed"]:
                    funcs[name] = (vm,fn)
                else:
                    success = False
            except Exception as exc:
                entries[name] = {"correctness":{"passed":False},"error":f"{type(exc).__name__}: {exc}"}
                success = False
        if len(funcs)==2:
            samples = {name: [] for name in funcs}
            for name, (_,fn) in funcs.items():
                for _ in range(args.warmup):
                    fn(gpu_a,gpu_b); dev.sync()
            for round_idx in range(args.rounds):
                order = ("default","mapped") if round_idx % 2 == 0 else ("mapped","default")
                for name in order:
                    fn = funcs[name][1]
                    times=[]
                    for _ in range(args.repeat):
                        start=perf_counter_ns(); fn(gpu_a,gpu_b); dev.sync()
                        times.append((perf_counter_ns()-start)/1e6)
                    samples[name].append(times)
            for name in funcs:
                flat=np.asarray(samples[name]).ravel()
                entries[name]["inference"]={"samples_ms":samples[name],"median_ms":float(np.median(flat)),"p95_ms":float(np.percentile(flat,95))}
            entries["mapped"]["speedup_vs_default"] = entries["default"]["inference"]["median_ms"]/entries["mapped"]["inference"]["median_ms"]
        records.append({"shape":{"M":m,"K":k,"N":n}, "input_sha256":hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest(),"stages":entries})
    try:
        driver = subprocess.check_output(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True, timeout=5).strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError, IndexError):
        driver = None
    report={"recorded_at_utc":datetime.now(timezone.utc).isoformat(),"git":_git_info(),"environment":collect_report(),"gpu":{"name":dev.device_name,"compute_version":dev.compute_version,"driver_version":driver,"device_index":0,"profiler_ncu_available":shutil.which("ncu") is not None},"seed":args.seed,"warmup":args.warmup,"repeat":args.repeat,"rounds":args.rounds,"results":records,"method":"Relax VM wall time; preallocated inputs, output allocation and device.sync per invocation included; alternating order per round. No profiler or GPU clock isolation; not kernel-only latency."}
    (args.output_dir/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    print(f"CUDA MatMul report: {args.output_dir / 'report.json'}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
