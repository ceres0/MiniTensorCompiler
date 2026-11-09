"""TVM 0.27.0.post1 CPU default build pipeline plus FuseTIR.

The installed default pipeline hides its Sequential inside a module-pass
callback, so this mirrors its exact pass order with one additional FuseTIR
immediately after LegalizeOps. This is version-specific, not a generic API.
"""

import tvm
from tvm import relax
from tvm.relax import backend


def linear_fused_pipeline():
    """Construct the pinned default pipeline with FuseTIR inserted once."""
    if tvm.__version__ != "0.27.0.post1":
        raise RuntimeError("linear fused pipeline requires apache-tvm 0.27.0.post1")

    @tvm.transform.module_pass(opt_level=0, name="MiniCompilerLinearFusedPipeline")
    def pipeline(mod, _ctx):
        transform = relax.transform
        return tvm.transform.Sequential([
            backend.DispatchSampling(),
            backend.DispatchSortScan(),
            transform.LegalizeOps(),
            transform.FuseTIR(),
            transform.RewriteDataflowReshape(),
            transform.ToNonDataflow(),
            transform.RemovePurityChecking(),
            transform.CallTIRRewrite(),
            transform.StaticPlanBlockMemory(),
            transform.RewriteCUDAGraph(),
            transform.LowerAllocTensor(),
            transform.KillAfterLastUse(),
            transform.LowerRuntimeBuiltin(),
            transform.ComputePrimValue(),
            transform.VMShapeLower(),
            transform.AttachGlobalSymbol(),
        ])(mod)
    return pipeline
