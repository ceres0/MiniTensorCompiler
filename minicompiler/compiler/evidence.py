"""Export inspectable CPU compilation evidence for one ONNX model.

Inspection lowering is independent from compilation: it never becomes input to
``tvm.compile``. The executable and its native source are from the real build.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import tvm
from tvm import relax

from minicompiler.compiler.pipeline import compile_module
from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.doctor import collect_report
from minicompiler.profiling.report import _git_info


def _native_sources(root, fmt):
    modules = []
    def visit(module):
        if module.kind == "llvm":
            modules.append(module)
        for child in module.imports:
            visit(child)
    visit(root)
    if not modules:
        return None, "No LLVM module exposed by executable"
    chunks, errors = [], []
    for i, module in enumerate(modules):
        try:
            source = module.inspect_source(fmt)
            if source:
                chunks.append(f"; LLVM module {i}\n{source}")
            else:
                errors.append(f"module {i}: empty source")
        except Exception as exc:
            errors.append(f"module {i}: {type(exc).__name__}: {exc}")
    if errors:
        # Do not label an incomplete set of modules as complete source evidence.
        return None, "; ".join(errors)
    return "\n".join(chunks), None


def export_evidence(model_path, output_dir, *, pass_mode="linear"):
    """Create inspection and build evidence; return (manifest, executable, summary).

    pass_mode selects ``linear``, ``reshape``, ``scheduled`` or ``none``. No output directory
    may exist, preventing old evidence from being mistaken for a new build.
    LLVM/assembly are emitted only if all LLVM source modules are available.
    """
    if pass_mode not in ("none", "reshape", "linear", "scheduled"):
        raise ValueError("pass_mode must be none, reshape, linear, or scheduled")
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"output directory exists: {output}")
    model, summary = load_and_summarize(model_path)
    before = import_relax(model, keep_params_in_input=False)
    if pass_mode == "linear":
        from minicompiler.passes.linear_bias_relu import run_linear_bias_relu
        after, pass_report = run_linear_bias_relu(before)
    elif pass_mode in ("reshape", "scheduled"):
        from minicompiler.passes.redundant_reshape import run_redundant_reshape
        after, pass_report = run_redundant_reshape(before)
        if pass_report["status"] == "failed":
            raise RuntimeError(f"reshape pass failed: {pass_report['error']}")
        if pass_mode == "scheduled":
            from minicompiler.compiler.scheduled_matmul import run_scheduled_matmul
            reshape_report = pass_report
            after, schedule_report = run_scheduled_matmul(after, stage="vectorize")
            pass_report = {"status": schedule_report["status"], "error": schedule_report["error"],
                           "reshape": reshape_report, "schedule": schedule_report}
    else:
        after, pass_report = before, {"enabled": False, "status": "disabled", "rewrites": 0}
    if pass_report["status"] == "failed":
        raise RuntimeError(f"{pass_mode} pass failed: {pass_report['error']}")
    # This intermediate is only a structural inspection of the post-pass IR.
    # Compilation below starts again from high-level `after`, not this module.
    inspection = relax.transform.LegalizeOps()(after)
    if pass_mode == "linear":
        inspection = relax.transform.FuseTIR()(inspection)
    executable, compile_ms, pipeline = compile_module(after, target="llvm", mode="custom" if pass_mode == "linear" else "default")
    vm_text = executable.as_text()
    llvm, llvm_error = _native_sources(executable.mod, "ll")
    assembly, asm_error = _native_sources(executable.mod, "asm")

    output.mkdir(parents=True)
    files = {"onnx_summary": "00_onnx_summary.json", "relax_imported": "01_relax_imported.py",
             "relax_after_pass": "02_relax_after_pass.py", "legalized_inspection": "03_legalized_inspection.py",
             "vm": "04_vm.txt"}
    (output / files["onnx_summary"]).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / files["relax_imported"]).write_text(before.script() + "\n", encoding="utf-8")
    (output / files["relax_after_pass"]).write_text(after.script() + "\n", encoding="utf-8")
    (output / files["legalized_inspection"]).write_text(inspection.script() + "\n", encoding="utf-8")
    (output / files["vm"]).write_text(vm_text + "\n", encoding="utf-8")
    availability = {}
    for name, text, error, filename in (("llvm_ir", llvm, llvm_error, "05_llvm.ll"),
                                        ("assembly", assembly, asm_error, "06_assembly.s")):
        availability[name] = {"available": text is not None, "reason": error}
        if text is not None:
            files[name] = filename
            (output / filename).write_text(text, encoding="utf-8")
    scheduled = {"available": False, "reason": "Standalone MatMul schedule is not integrated into this model pipeline"}
    if pass_mode == "scheduled":
        count = pass_report["schedule"]["rewrites"]
        scheduled = {"available": count > 0, "rewrites": count,
                     "reason": None if count else "No eligible MatMul was found"}
        if count:
            files["scheduled_tir"] = "07_scheduled_tir.py"
            (output / files["scheduled_tir"]).write_text(after.script() + "\n", encoding="utf-8")
    manifest = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(), "git": _git_info(),
        "environment": collect_report(),
        "model": str(model_path),
        "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        "model_hash_scope": "ONNX file only; external data files excluded",
        "pass_mode": pass_mode, "pass_report": pass_report,
        "compilation": {"target": "llvm", "compile_ms": compile_ms, "pipeline": pipeline},
        "files": files, "availability": availability,
        "legalized_inspection_note": "Independent LegalizeOps" + (" and FuseTIR" if pass_mode == "linear" else "") + "; compilation starts from high-level post-pass module, not this inspection IR.",
        "scheduled_tir": scheduled,
        "ownership": "ONNX importer, lowering, LLVM codegen and VM are provided by TVM; project passes and evidence collection are custom.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest, executable, summary
