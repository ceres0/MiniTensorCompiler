"""Instrument real TVM pass invocations without running a second pipeline.

Inclusive timings nest, so they must never be summed as a compile duration.
Exclusive timings subtract nested instrumented calls, but include instrumentation
and callback overhead. Native code generation outside passes is not measured here.
"""

from collections import defaultdict
import threading
import time

import tvm


@tvm.instrument.pass_instrument
class PassTimer:
    """Record wall times and selected static IR counts during a PassContext.

    Use a fresh instance for each compilation and pass it as an instrument to
    the *existing* PassContext. `snapshot()` is JSON-serializable. Counts after
    LegalizeOps and FuseTIR describe static PrimFuncs, not runtime kernel calls.
    """

    def __init__(self):
        self._local = threading.local()
        self._lock = threading.Lock()
        self._events = []
        self._counts = []
        self._open = 0

    def run_before_pass(self, mod, info):
        stack = getattr(self._local, "stack", None)
        if stack is None:
            stack = self._local.stack = []
        stack.append({"name": str(info.name), "start": time.perf_counter_ns(), "child_ns": 0})
        with self._lock:
            self._open += 1

    def run_after_pass(self, mod, info):
        end = time.perf_counter_ns()
        stack = getattr(self._local, "stack", [])
        if not stack:
            # Do not affect compilation if TVM calls are unbalanced.
            return
        entry = stack.pop()
        elapsed = max(0, end - entry["start"])
        if stack:
            stack[-1]["child_ns"] += elapsed
        event = {"name": entry["name"], "depth": len(stack),
                 "inclusive_ms": elapsed / 1e6,
                 "exclusive_ms": max(0, elapsed - entry["child_ns"]) / 1e6}
        count = None
        if entry["name"] in ("LegalizeOps", "FuseTIR"):
            count = {"after_pass": entry["name"],
                     "tir_primfunc_count": sum(isinstance(func, tvm.tirx.PrimFunc)
                                               for func in mod.functions.values())}
        with self._lock:
            self._open -= 1
            self._events.append(event)
            if count is not None:
                self._counts.append(count)

    def snapshot(self):
        """Return completed invocations and per-name totals without inventing missing timings."""
        with self._lock:
            events = [dict(event) for event in self._events]
            counts = [dict(item) for item in self._counts]
            incomplete = self._open
        totals = defaultdict(lambda: {"calls": 0, "inclusive_ms": 0.0, "exclusive_ms": 0.0})
        for event in events:
            item = totals[event["name"]]
            item["calls"] += 1
            item["inclusive_ms"] += event["inclusive_ms"]
            item["exclusive_ms"] += event["exclusive_ms"]
        return {"events": events, "by_pass": dict(totals), "static_ir_snapshots": counts,
                "incomplete_passes": incomplete,
                "timing_note": "Instrumented wall time includes callback overhead; inclusive pass times overlap. Do not sum inclusive times.",
                "runtime_kernel_invocations": None}
