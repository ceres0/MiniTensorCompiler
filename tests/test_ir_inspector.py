import json

import pytest
import tvm
from tvm.script import relax as R
from tvm.relax import dpl

from minicompiler.ir import UnknownShapeError, inspect_module


@tvm.script.ir_module
class StaticGraph:
    @R.function
    def main(x: R.Tensor((2, 3), "float32"), y: R.Tensor((3, 4), "float32")):
        with R.dataflow():
            matmul = R.matmul(x, y)
            activated = R.nn.relu(matmul)
            R.output(activated)
        return activated


@tvm.script.ir_module
class DynamicGraph:
    @R.function
    def main(x: R.Tensor(("n", 4), "float32")):
        return R.nn.relu(x)


def test_inspects_calls_shapes_and_cross_binding_pattern():
    relu_matmul = dpl.is_op("relax.nn.relu")(
        dpl.is_op("relax.matmul")(dpl.wildcard(), dpl.wildcard())
    )
    report = inspect_module(StaticGraph)
    func = report["functions"]["main"]
    assert report["relax_calls"] == 2
    assert func["operators"] == {"relax.matmul": 1, "relax.nn.relu": 1}
    assert func["dfpattern_matches"]["matmul"] == func["dfpattern_matches"]["relu"] == 1
    assert func["calls"][0]["result"]["shape"] == [2, 4]
    assert func["return_type"]["dtype"] == "float32"
    assert inspect_module(StaticGraph, {"relu_matmul": relu_matmul})["functions"]["main"]["dfpattern_matches"] == {"relu_matmul": 1}
    json.dumps(report)


def test_symbolic_shape_is_rejected():
    with pytest.raises(UnknownShapeError, match="not static"):
        inspect_module(DynamicGraph)
