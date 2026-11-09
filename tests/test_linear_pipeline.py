"""Guard the pinned default pipeline mirror and compare real compiled outputs."""

import ast
import inspect

import numpy as np
import pytest
import tvm
from tvm import relax
from tvm.relax import pipeline

from minicompiler.compiler.linear_pipeline import linear_fused_pipeline
from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.passes.linear_bias_relu import run_linear_bias_relu


def sequential_calls(function):
    tree = ast.parse(inspect.getsource(function))
    seq = next(node for node in ast.walk(tree) if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Attribute) and node.func.attr == "Sequential")
    return [ast.unparse(item.func) for item in seq.args[0].elts]


def test_pipeline_tracks_pinned_default_and_inserts_fusetir_once():
    default = sequential_calls(pipeline.default_build_pipeline)
    custom = sequential_calls(linear_fused_pipeline)
    assert custom.count("transform.FuseTIR") == 1
    assert custom.index("transform.FuseTIR") == custom.index("transform.LegalizeOps") + 1
    custom.remove("transform.FuseTIR")
    assert custom == default


def test_linear_fused_pipeline_matches_default_on_mlp(tmp_path):
    pytest.importorskip("torch")
    from models.export import export_model
    path = export_model("mlp", tmp_path / "mlp.onnx", batch=1, seed=17)
    model, _ = load_and_summarize(path)
    mod = import_relax(model)
    fused, report = run_linear_bias_relu(mod)
    assert report["status"] == "ok" and report["rewrites"] == 1
    input_data = np.random.default_rng(13).standard_normal((1, 128), dtype=np.float32)
    outputs = []
    for module, pipeline_arg in ((mod, "default"), (fused, linear_fused_pipeline())):
        ex = tvm.compile(module, target="llvm", relax_pipeline=pipeline_arg)
        vm = relax.VirtualMachine(ex, tvm.cpu())
        outputs.append(vm["main"](tvm.runtime.tensor(input_data)).numpy())
    np.testing.assert_allclose(outputs[1], outputs[0], rtol=1e-4, atol=1e-5)
