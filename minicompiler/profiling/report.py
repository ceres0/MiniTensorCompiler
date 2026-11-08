"""End-to-end CPU baseline reporting for the benchmark CLI."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from time import perf_counter_ns

import onnxruntime as ort
import tvm

from minicompiler.doctor import collect_report
from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.profiling.benchmark import measure
from minicompiler.runtime.correctness import compare_outputs, create_ort_runner, make_inputs
from minicompiler.runtime.runner import build_runner


def _git_info():
    project_root = Path(__file__).resolve().parents[2]
    def run(*args):
        try:
            return subprocess.check_output(["git", "-C", str(project_root), *args], stderr=subprocess.DEVNULL, text=True, timeout=5).strip()
        except (OSError, subprocess.SubprocessError):
            return None
    commit = run("rev-parse", "HEAD")
    status = run("status", "--porcelain") if commit else None
    return {"commit": commit, "dirty": bool(status) if status is not None else None}


def run_benchmark(model_path, *, target="llvm", mode="default", threads=1, seed=0,
                  warmup=30, repeat=100, rounds=3):
    """Build one embedded-parameter TVM baseline and compare with ORT CPU.

    The CLI configures thread environment before importing this module. Python
    API callers must do likewise before the TVM runtime initializes.
    """
    if threads < 1 or seed < 0 or warmup < 0 or repeat < 1 or rounds < 1:
        raise ValueError("invalid thread, seed, or iteration count")
    model_path = Path(model_path)
    start = perf_counter_ns()
    model, summary = load_and_summarize(model_path)
    mod = import_relax(model, keep_params_in_input=False)
    import_ms = (perf_counter_ns() - start) / 1e6
    runner = build_runner(mod, mode=mode, target=target,
                          onnx_input_names=[entry["name"] for entry in summary["inputs"]])
    actual_threads = tvm.runtime.num_threads()
    if actual_threads != threads:
        raise RuntimeError(f"TVM runtime reports {actual_threads} threads; requested {threads}. "
                           "Start a fresh process with TVM_NUM_THREADS set before importing TVM.")
    inputs = make_inputs(summary, seed)
    prepared = runner.prepare_inputs(inputs)
    ort_run = create_ort_runner(model_path, threads=threads)
    reference = ort_run(inputs)
    actual = runner.outputs_to_numpy(runner.run_prepared(prepared))
    correctness = compare_outputs(actual, reference)
    # Correctness is evaluated before collecting any performance measurements.
    # ORT returns NumPy arrays while TVM returns runtime tensors; no explicit
    # conversion or input copying is included in either timed callable.
    inference = None
    if correctness["passed"]:
        inference = {
            "tvm": measure(lambda: runner.run_prepared(prepared), warmup, repeat, rounds),
            "ort": measure(lambda: ort_run(inputs), warmup, repeat, rounds),
            "timing_scope": "Python API call including runtime output allocation; prepared inputs, model/session setup and explicit TVM-to-NumPy conversion excluded. ORT returns NumPy arrays directly.",
        }
    environment = collect_report()
    environment.update({"requested_threads": threads, "tvm_runtime_threads": actual_threads,
                        "ort_intra_op_threads": threads, "ort_inter_op_threads": 1,
                        "ort_provider": "CPUExecutionProvider", "onnxruntime_version": ort.__version__,
                        "cpu_affinity": "not controlled", "power_policy": "not controlled"})
    return {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "git": _git_info(),
        "environment": environment,
        "model": {"path": str(model_path), "sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
                  "sha256_scope": "ONNX file only; external tensor data excluded",
                  "inputs": summary["inputs"], "opsets": summary["opsets"], "input_seed": seed,
                  "input_distribution": "numpy default_rng standard_normal float32", "weights": "embedded ONNX initializers"},
        "pipeline": runner.pipeline,
        "correctness": correctness,
        "compilation": {"onnx_load_check_shape_inference_and_import_ms": import_ms,
                        "tvm_compile_ms": runner.compile_time_ms},
        "inference": inference,
    }
