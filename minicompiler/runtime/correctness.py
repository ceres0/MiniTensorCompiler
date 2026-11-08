"""Deterministic FP32 inputs and ONNX Runtime correctness reference."""

import numpy as np
import onnxruntime as ort


def make_inputs(summary, seed=0):
    """Generate deterministic standard-normal FP32 inputs in ONNX input order."""
    rng = np.random.default_rng(seed)
    return {item["name"]: rng.standard_normal(item["shape"], dtype=np.float32)
            for item in summary["inputs"]}


def create_ort_runner(model_path, threads=1):
    """Construct an ORT CPU-only callable; session setup is outside timed runs."""
    if threads < 1:
        raise ValueError("threads must be positive")
    options = ort.SessionOptions()
    options.intra_op_num_threads = threads
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(str(model_path), sess_options=options,
                                   providers=["CPUExecutionProvider"])
    def run(inputs):
        return session.run(None, inputs)
    return run


def compare_outputs(actual, expected, rtol=1e-4, atol=1e-5):
    """Compare ordered model outputs, returning JSON-safe error metrics.

    Relative error is abs(actual-reference)/max(abs(reference), 1e-12). This
    diagnostic definition is separate from numpy's allclose acceptance rule.
    A numerical mismatch is reported as passed=False instead of hiding metrics.
    Shape/count mismatches are errors and are never broadcast.
    """
    if rtol < 0 or atol < 0:
        raise ValueError("tolerances must be nonnegative")
    if len(actual) != len(expected) or not expected:
        raise ValueError("output count mismatch or no outputs")
    diffs, rels = [], []
    passed = True
    nonfinite = False
    for index, (got, ref) in enumerate(zip(actual, expected, strict=True)):
        got, ref = np.asarray(got), np.asarray(ref)
        if got.shape != ref.shape:
            raise ValueError(f"output {index} shape mismatch: {got.shape} != {ref.shape}")
        if not np.isfinite(got).all() or not np.isfinite(ref).all():
            nonfinite = True
            passed = False
            continue
        try:
            np.testing.assert_allclose(got, ref, rtol=rtol, atol=atol, equal_nan=False)
        except AssertionError:
            passed = False
        difference = np.abs(got.astype(np.float64) - ref.astype(np.float64)).ravel()
        diffs.append(difference)
        rels.append(difference / np.maximum(np.abs(ref.astype(np.float64).ravel()), 1e-12))
    if nonfinite:
        max_abs = max_rel = rmse = None
    else:
        errors = np.concatenate(diffs)
        relative = np.concatenate(rels)
        max_abs = float(np.max(errors, initial=0))
        max_rel = float(np.max(relative, initial=0))
        rmse = float(np.sqrt(np.mean(errors ** 2))) if errors.size else 0.0
    return {"passed": passed, "rtol": rtol, "atol": atol,
            "max_abs_error": max_abs, "max_rel_error": max_rel, "rmse": rmse,
            "relative_error_floor": 1e-12}
