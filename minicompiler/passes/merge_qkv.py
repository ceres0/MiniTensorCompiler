"""Experimental QKV packing for a deliberately narrow, statically proved case.

Disabled by default. The caller must explicitly supply measured (M, K, N)
shapes in an allowlist; this module makes no claim that a shape is faster.
"""

import numpy as np
import tvm
from tvm import relax


def _static_shape(ty):
    if not isinstance(ty, relax.TensorType) or str(ty.dtype) != "float32":
        return None
    if not isinstance(ty.shape, relax.ShapeExpr):
        return None
    dims = []
    for dim in ty.shape:
        if not isinstance(dim, tvm.tirx.IntImm) or int(dim.value) <= 0:
            return None
        dims.append(int(dim.value))
    return tuple(dims)


def _candidate(bindings):
    if len(bindings) != 3 or any(not isinstance(b, relax.VarBinding) for b in bindings):
        return None
    calls = [b.value for b in bindings]
    if any(not isinstance(c, relax.Call) or not isinstance(c.op, tvm.ir.Op)
           or c.op.name != "relax.matmul" or len(c.args) != 2 for c in calls):
        return None
    source = calls[0].args[0]
    if not isinstance(source, relax.Var) or any(not c.args[0].same_as(source) for c in calls):
        return None
    if any(not isinstance(c.args[1], tvm.ir.GenericConst) for c in calls):
        return None
    shape = _static_shape(source.ty)
    weights = [_static_shape(c.args[1].ty) for c in calls]
    outputs = [_static_shape(b.var.ty) for b in bindings]
    if shape is None or len(shape) != 2 or any(w is None or len(w) != 2 for w in weights):
        return None
    m, k = shape
    n = weights[0][1]
    if any(w != (k, n) for w in weights) or any(o != (m, n) for o in outputs):
        return None
    # Reject an explicit non-FP32 accumulator/output dtype, even if malformed IR
    # reports an FP32 output type.
    if any(str(c.attrs.out_dtype) not in ("", "void", "float32", "None") for c in calls):
        return None
    return source, (m, k, n), [c.args[1].value.numpy() for c in calls]


def run_merge_qkv(mod, *, enabled=False, allowed_shapes=()):
    """Pack three adjacent same-input constant projections, gated by shape.

    Returns (module, report). Existing bindings and consumers retain their vars;
    only adjacent dataflow MatMuls are considered. Pass errors roll back fully.
    An allowlisted shape is an explicit caller decision, not proof of a speedup.
    """
    report = {"enabled": bool(enabled), "status": "disabled" if not enabled else "ok",
              "matches": 0, "rewrites": 0, "skipped_not_allowlisted": 0,
              "events": [], "error": None}
    if not enabled:
        return mod, report
    allowed = {tuple(shape) for shape in allowed_shapes}
    try:
        out = mod.clone()
        for gv, func in mod.functions.items():
            if not isinstance(func, relax.Function) or not isinstance(func.body, relax.SeqExpr):
                continue
            if func.attrs is not None and "Primitive" in func.attrs and int(func.attrs["Primitive"]) != 0:
                continue
            blocks, changed = [], False
            for block in func.body.blocks:
                if not isinstance(block, relax.DataflowBlock):
                    blocks.append(block)
                    continue
                original, new = list(block.bindings), []
                i = 0
                while i < len(original):
                    selected = original[i:i + 3]
                    match = _candidate(selected)
                    if match is None:
                        new.append(original[i]); i += 1; continue
                    source, shape, weights = match
                    report["matches"] += 1
                    if shape not in allowed:
                        report["skipped_not_allowlisted"] += 1
                        report["events"].append({"action": "skipped", "shape": list(shape), "reason": "shape not allowlisted"})
                        new.extend(selected); i += 3; continue
                    m, k, n = shape
                    merged = relax.DataflowVar("qkv_packed", relax.TensorType((m, 3 * n), "float32"))
                    packed = relax.const(np.concatenate(weights, axis=1))
                    new.append(relax.VarBinding(merged, relax.op.matmul(source, packed)))
                    for j, binding in enumerate(selected):
                        value = relax.op.strided_slice(merged, axes=[1], begin=[j*n], end=[(j+1)*n])
                        new.append(relax.VarBinding(binding.var, value))
                    report["events"].append({"action": "rewritten", "shape": list(shape)})
                    report["rewrites"] += 1
                    changed = True; i += 3
                blocks.append(relax.DataflowBlock(new) if changed else block)
            if changed:
                body = relax.SeqExpr(blocks, func.body.body)
                updated = relax.Function(func.params, body, func.ret_ty, func.is_pure, func.attrs, func.span)
                out.update_func(gv, updated)
        if report["rewrites"]:
            out = relax.transform.Normalize()(out)
            relax.analysis.well_formed(out)
        return out, report
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["attempted_rewrites"] = report["rewrites"]
        report["rewrites"] = 0
        for event in report["events"]:
            if event["action"] == "rewritten":
                event["action"] = "rolled_back"
        return mod, report
