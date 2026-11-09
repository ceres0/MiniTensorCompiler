"""Reproduce CPU model baselines and a TensorIR ablation in one command.

Run with the project's locked dev and models extras installed, for example:
    python -m benchmarks.run_suite --output-dir runs/suite
Each subprocess uses the same thread settings and independent fresh runtime.
"""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--repeat", type=int, default=100)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--shape", default="8,128,128", help="one MatMul M,K,N shape")
    args = parser.parse_args(argv)
    if args.threads < 1 or args.seed < 0 or args.warmup < 0 or args.repeat < 1 or args.rounds < 1:
        parser.error("threads, repeat and rounds must be positive; seed and warmup must be nonnegative")
    try:
        shape = tuple(int(x) for x in args.shape.split(","))
        if len(shape) != 3 or min(shape) <= 0:
            raise ValueError()
    except ValueError:
        parser.error("--shape must be a positive M,K,N triple")
    out = args.output_dir.resolve()
    if out.exists():
        parser.error("output directory exists; choose a new directory")
    # Reserve the directory once, without touching any existing artifacts.
    out.mkdir(parents=True)
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.update(TVM_NUM_THREADS=str(args.threads), OMP_NUM_THREADS=str(args.threads),
               OPENBLAS_NUM_THREADS=str(args.threads))
    timings = ["--threads", str(args.threads), "--seed", str(args.seed), "--warmup", str(args.warmup),
               "--repeat", str(args.repeat), "--rounds", str(args.rounds)]
    model = {name: out / "models" / f"{name}.onnx" for name in ("mlp", "cnn")}
    py = sys.executable
    steps = []
    for name in ("mlp", "cnn"):
        steps.append((f"export_{name}", [py, "-m", f"models.generate_{name}", "--output", str(model[name]), "--seed", str(args.seed)]))
        steps.append((f"bench_{name}", [py, "-m", "minicompiler", "bench", "--model", str(model[name]),
                                       "--target", "llvm", "--mode", "custom", "--output", str(out / f"{name}.json"), *timings]))
    steps.append(("bench_mlp_nofusion", [py, "-m", "minicompiler", "bench", "--model", str(model["mlp"]),
                                          "--target", "llvm", "--mode", "nofusion", "--output", str(out / "mlp_nofusion.json"), *timings]))
    steps.append(("matmul_ablation", [py, "-m", "benchmarks.matmul_schedule", "--output-dir", str(out / "matmul"),
                                      "--shape", ",".join(map(str, shape)), *timings]))
    try:
        commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    versions = {}
    for name in ("apache-tvm", "numpy", "onnx", "onnxruntime", "torch"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "git": {"commit": commit, "dirty": dirty},
              "python": sys.version, "packages": versions,
              "parameters": {"threads": args.threads, "seed": args.seed, "warmup": args.warmup,
                             "repeat": args.repeat, "rounds": args.rounds, "matmul_shape": list(shape)},
              "status": "running", "steps": [],
              "outputs": {"mlp": "mlp.json", "cnn": "cnn.json", "mlp_nofusion": "mlp_nofusion.json", "matmul": "matmul/report.json"}}
    for name, cmd in steps:
        try:
            completed = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
        except OSError as exc:
            completed = subprocess.CompletedProcess(cmd, 1, "", f"{type(exc).__name__}: {exc}")
        (out / f"{name}.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (out / f"{name}.stderr.log").write_text(completed.stderr, encoding="utf-8")
        report["steps"].append({"name": name, "argv": cmd, "returncode": completed.returncode,
                                "stdout": f"{name}.stdout.log", "stderr": f"{name}.stderr.log"})
        if completed.returncode:
            report["status"] = "failed"
            break
    else:
        report["status"] = "ok"
    (out / "suite.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Suite {report['status']}: {out / 'suite.json'}")
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
