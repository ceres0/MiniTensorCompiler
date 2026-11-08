"""Wall-clock inference timing; model loading and compilation are excluded."""

from time import perf_counter_ns
import numpy as np


def measure(fn, warmup=30, repeat=100, rounds=3):
    """Run warmups then independent rounds of single-call wall-clock timings.

    Returned samples are milliseconds, retained by round; summaries cover all
    measured samples. The caller controls exactly what `fn` includes (e.g.
    output materialization), and must synchronize asynchronous devices itself.
    """
    if warmup < 0 or repeat < 1 or rounds < 1:
        raise ValueError("warmup must be nonnegative and repeat/rounds positive")
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(rounds):
        current = []
        for _ in range(repeat):
            start = perf_counter_ns()
            fn()
            current.append((perf_counter_ns() - start) / 1_000_000)
        samples.append(current)
    flat = np.asarray(samples, dtype=np.float64).ravel()
    return {"warmup": warmup, "repetitions_per_round": repeat, "rounds": rounds,
            "samples_ms": samples, "median_ms": float(np.median(flat)),
            "p95_ms": float(np.percentile(flat, 95))}
