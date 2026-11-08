"""Inspect normalized Relax calls using TVM's visitor and dataflow patterns.

The default patterns match individual calls, not multi-binding fused subgraphs.
No optimization or assumption about unknown dimensions is made here.
"""

from collections import Counter

import tvm
from tvm import relax
from tvm.relax import dpl


class UnknownShapeError(ValueError):
    """A tensor type lacks a fully static shape or a concrete dtype."""


def _describe_type(ty, location):
    if isinstance(ty, relax.TensorType):
        shape = ty.shape
        if not isinstance(shape, relax.ShapeExpr):
            raise UnknownShapeError(f"{location}: tensor shape is unknown: {ty}")
        dimensions = []
        for dim in shape:
            if not isinstance(dim, tvm.tirx.IntImm):
                raise UnknownShapeError(f"{location}: tensor dimension is not static: {dim}")
            dimensions.append(int(dim.value))
        dtype = str(ty.dtype)
        if not dtype or dtype == "void":
            raise UnknownShapeError(f"{location}: tensor dtype is unknown")
        return {"kind": "tensor", "shape": dimensions, "dtype": dtype}
    if isinstance(ty, relax.TupleType):
        return {"kind": "tuple", "fields": [_describe_type(field, location) for field in ty.fields]}
    if ty is None:
        raise UnknownShapeError(f"{location}: type is unavailable")
    return {"kind": "other", "type": str(ty)}


def _default_patterns():
    wildcard = dpl.wildcard
    return {
        "matmul": dpl.is_op("relax.matmul")(wildcard(), wildcard()),
        "add": dpl.is_op("relax.add")(wildcard(), wildcard()),
        "relu": dpl.is_op("relax.nn.relu")(wildcard()),
        "reshape": dpl.is_op("relax.reshape")(wildcard(), wildcard()),
    }


@relax.expr_functor.visitor
class _CallVisitor(relax.PyExprVisitor):
    def __init__(self, patterns, var2val, function_name):
        super().__init__()
        self.patterns = patterns
        self.var2val = var2val
        self.function_name = function_name
        self.calls = []
        self.operators = Counter()
        self.matches = Counter({name: 0 for name in patterns})
        self.errors = []

    def visit_call_(self, call):
        op = call.op.name if isinstance(call.op, tvm.ir.Op) else str(call.op)
        location = f"{self.function_name}: call {op}"
        try:
            result = _describe_type(call.ty, location)
        except UnknownShapeError as exc:
            # TVM's FFI translates Python exceptions raised inside visitor
            # callbacks to RuntimeError. Raise the original type after traversal.
            self.errors.append(str(exc))
            result = None
        self.calls.append({"op": op, "result": result})
        self.operators[op] += 1
        for name, pattern in self.patterns.items():
            if pattern.match(call, self.var2val):
                self.matches[name] += 1
        super().visit_call_(call)


def inspect_module(mod, patterns=None):
    """Return JSON-serializable call and pattern statistics for each Relax function.

    ``patterns`` optionally maps names to Relax DFPattern objects; matching uses
    TVM's variable-to-binding map, so callers may supply multi-binding patterns.
    Unknown tensor shapes, symbolic dimensions, and unknown dtypes raise
    :class:`UnknownShapeError` rather than being treated as static.
    """
    patterns = _default_patterns() if patterns is None else patterns
    functions = {}
    for global_var, func in mod.functions.items():
        if not isinstance(func, relax.Function):
            continue
        name = global_var.name_hint
        visitor = _CallVisitor(patterns, relax.analysis.get_var2val(func), name)
        visitor.visit_expr(func)
        if visitor.errors:
            raise UnknownShapeError(visitor.errors[0])
        functions[name] = {
            "parameters": [{"name": str(param.name), "type": _describe_type(param.ty, f"{name}: parameter {param.name}")} for param in func.params],
            "return_type": _describe_type(func.ret_ty, f"{name}: return"),
            "relax_calls": len(visitor.calls),
            "operators": dict(sorted(visitor.operators.items())),
            "dfpattern_matches": dict(visitor.matches),
            "calls": visitor.calls,
        }
    return {"relax_calls": sum(f["relax_calls"] for f in functions.values()), "functions": functions}
