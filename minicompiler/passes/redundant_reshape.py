"""Conservatively collapse two consecutive pure Relax reshapes.

Only fully static shapes with positive dimensions (or scalar shape) are
rewritten. In particular, empty tensors are skipped because literal zero in a
Relax reshape target can have input-dependent semantics. The final target is
reconstructed from the proved result type rather than moved from the old call.
"""

import math

import tvm
from tvm import relax
from tvm.relax.dpl import is_op, rewrite_call, wildcard


def _tensor_description(expr):
    ty = getattr(expr, "ty", None)
    if not isinstance(ty, relax.TensorType):
        return None, "not a tensor or type unavailable"
    if not isinstance(ty.shape, relax.ShapeExpr):
        return None, "unknown shape"
    shape = []
    for dim in ty.shape:
        if not isinstance(dim, tvm.tirx.IntImm):
            return None, "symbolic shape"
        size = int(dim.value)
        if size <= 0:
            return None, "zero or negative dimension"
        shape.append(size)
    dtype = str(ty.dtype)
    if not dtype or dtype == "void":
        return None, "unknown dtype"
    return (tuple(shape), dtype), None


def run_redundant_reshape(mod, *, enabled=True):
    """Run the Relax function pass and return ``(new_module, report)``.

    The report is independent per invocation. Each match is either rewritten or
    skipped with a reason. The original module is not mutated. The underlying
    DPL rewriter removes dead bindings and preserves live/shared consumers.
    """
    report = {"enabled": bool(enabled), "status": "disabled" if not enabled else "ok",
              "error": None, "matches": 0, "rewrites": 0,
              "attempted_rewrites": 0, "skipped": 0, "events": []}
    if not enabled:
        return mod, report

    source, first_shape, final_shape = wildcard(), wildcard(), wildcard()
    inner = is_op("relax.reshape")(source, first_shape)
    outer = is_op("relax.reshape")(inner, final_shape)

    def rewriter(original, matched):
        report["matches"] += 1
        descriptions = []
        for label, value in (("input", matched[source]), ("intermediate", matched[inner]),
                             ("output", original)):
            description, reason = _tensor_description(value)
            if reason:
                report["skipped"] += 1
                report["events"].append({"action": "skipped", "reason": f"{label}: {reason}"})
                return original
            descriptions.append(description)
        (input_shape, input_dtype), (mid_shape, mid_dtype), (out_shape, out_dtype) = descriptions
        if input_dtype != mid_dtype or input_dtype != out_dtype:
            reason = "dtype mismatch"
        elif len({math.prod(input_shape), math.prod(mid_shape), math.prod(out_shape)}) != 1:
            reason = "element count mismatch"
        else:
            reason = None
        if reason:
            report["skipped"] += 1
            report["events"].append({"action": "skipped", "reason": reason})
            return original
        # Construct a concrete target, avoiding re-interpretation of 0 or -1
        # against the original input after bypassing the intermediate reshape.
        result = relax.op.reshape(matched[source], relax.ShapeExpr(out_shape))
        report["rewrites"] += 1
        report["events"].append({"action": "rewritten", "input_shape": list(input_shape),
                                 "intermediate_shape": list(mid_shape), "output_shape": list(out_shape),
                                 "dtype": input_dtype})
        return result

    @relax.transform.function_pass(opt_level=0, name="MiniCompilerCollapseReshape")
    def reshape_pass(func, _mod, _ctx):
        if func.attrs is not None and "Primitive" in func.attrs and int(func.attrs["Primitive"]) != 0:
            return func
        return rewrite_call(outer, rewriter, func)

    try:
        result = reshape_pass(mod)
    except Exception as exc:
        # A function pass can fail after processing an earlier function. Never
        # return that partial result: expose the failure and keep the input IR.
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["attempted_rewrites"] = report["rewrites"]
        report["rewrites"] = 0
        for event in report["events"]:
            if event["action"] == "rewritten":
                event["action"] = "rolled_back"
        return mod, report
    report["attempted_rewrites"] = report["rewrites"]
    return result, report
