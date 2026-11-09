"""Guarded Relax dataflow grouping for FP32 matrix multiply, bias and ReLU.

TVM's FuseOpsByPattern provides graph extraction. This project supplies the
pattern and conservative semantic guard; this does not promise faster kernels.
"""
import tvm
from tvm import relax
from tvm.relax.dpl import is_op, wildcard

_PATTERN_NAME = "minicompiler.linear_bias_relu"


def _shape(expr):
    ty = getattr(expr, "ty", None)
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


def _composite_calls(mod):
    composites = set()
    for gv, func in mod.functions.items():
        if (isinstance(func, relax.Function) and func.attrs is not None
                and "Composite" in func.attrs and str(func.attrs["Composite"]) == _PATTERN_NAME):
            composites.add(gv.name_hint)

    @relax.expr_functor.visitor
    class Visitor(relax.PyExprVisitor):
        def __init__(self):
            super().__init__()
            self.count = 0

        def visit_call_(self, call):
            if isinstance(call.op, tvm.ir.GlobalVar) and call.op.name_hint in composites:
                self.count += 1
            super().visit_call_(call)

    visitor = Visitor()
    for _, func in mod.functions.items():
        if isinstance(func, relax.Function):
            visitor.visit_expr(func)
    return visitor.count


def run_linear_bias_relu(mod, *, enabled=True):
    """Return (module, report); on failure roll back and report the exception.

    Supports 2D positive static FP32 x[M,K], w[K,N], b[N] in that operand
    order. Weight and bias can be either constants or runtime inputs. The
    enclosing chain must be in a dataflow block with no external uses of its
    intermediate matmul/add results. Fusion only groups a subgraph; TVM owns
    lowering and code generation.
    """
    report = {"enabled": bool(enabled), "status": "ok" if enabled else "disabled",
              "error": None, "matches": 0, "rewrites": 0, "skipped": 0, "events": []}
    if not enabled:
        return mod, report
    x, w, b = wildcard(), wildcard(), wildcard()
    mm = is_op("relax.matmul")(x, w)
    add = is_op("relax.add")(mm, b)
    out = is_op("relax.nn.relu")(add)

    def check(ctx):
        report["matches"] += 1
        expressions = ctx.annotated_expr
        shapes = {name: _shape(expressions[name]) for name in ("x", "w", "b", "mm", "add", "out")}
        reason = None
        if any(shape is None for shape in shapes.values()):
            reason = "requires static positive FP32 tensor shapes"
        elif len(shapes["x"]) != 2 or len(shapes["w"]) != 2 or len(shapes["b"]) != 1:
            reason = "requires x and weight rank 2 and bias rank 1"
        else:
            m, k = shapes["x"]
            wk, n = shapes["w"]
            if k != wk or shapes["b"] != (n,) or any(shapes[a] != (m, n) for a in ("mm", "add", "out")):
                reason = "matrix or bias shape mismatch"
        if reason is None:
            # DPL treats add as commutative, but this rule intentionally accepts
            # only matmul + bias. Inspect the actual operand order explicitly.
            mm_var = ctx.value_to_bound_var.get(expressions["mm"])
            lhs = expressions["add"].args[0]
            if not (lhs.same_as(expressions["mm"]) or (mm_var is not None and lhs.same_as(mm_var))):
                reason = "requires matmul as the left operand of add"
        if reason is None:
            # Fuse only when intermediate values have no users outside the
            # matched group. This preserves shared-use semantics conservatively.
            group = set(ctx.matched_bindings.keys())
            for label in ("mm", "add"):
                bound = ctx.value_to_bound_var.get(expressions[label])
                if bound is None or any(user not in group for user in ctx.var_usages.get(bound, [])):
                    reason = f"{label} has an external consumer or is not bound"
                    break
        if reason:
            report["skipped"] += 1
            report["events"].append({"action": "skipped", "reason": reason})
            return False
        report["events"].append({"action": "accepted", "input_shape": list(shapes["x"]),
                                 "weight_shape": list(shapes["w"]), "bias_shape": list(shapes["b"])})
        return True

    pattern = relax.transform.FusionPattern(
        _PATTERN_NAME, out, {"x": x, "w": w, "b": b, "mm": mm, "add": add, "out": out}, check)
    try:
        before = _composite_calls(mod)
        result = relax.transform.FuseOpsByPattern([pattern], bind_constants=False)(mod)
        report["rewrites"] = _composite_calls(result) - before
        return result, report
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["rewrites"] = 0
        return mod, report
