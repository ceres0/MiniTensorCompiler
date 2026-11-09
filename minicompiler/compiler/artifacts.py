"""Export and reload CPU VM executables with embedded ONNX initializers.

A compiled library is native code: load only artifacts from trusted sources.
The manifest hash detects accidental mismatches, not malicious modification.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import tempfile

import numpy as np
import tvm
from tvm import relax

from minicompiler.compiler.pipeline import compile_module
from minicompiler.frontend import import_relax, load_and_summarize
from minicompiler.runtime.runner import TVMRunner


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_onnx_artifact(model_path, output_dir, *, target="llvm", mode="default"):
    """Compile and export a self-contained LLVM CPU executable and manifest.

    Initializers are embedded during import, including loaded ONNX external data.
    No separate runtime parameter files are accepted. Refuse existing output.
    """
    if target != "llvm":
        raise ValueError("only the llvm CPU target is supported")
    if mode not in ("default", "nofusion", "custom", "scheduled"):
        raise ValueError(f"unsupported mode: {mode}")
    model_path, output_dir = Path(model_path), Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"output already exists: {output_dir}")
    model, summary = load_and_summarize(model_path)
    mod = import_relax(model, keep_params_in_input=False)
    custom_report = None
    schedule_report = None
    reshape_report = None
    if mode == "custom":
        from minicompiler.passes.linear_bias_relu import run_linear_bias_relu
        mod, custom_report = run_linear_bias_relu(mod)
        if custom_report["status"] != "ok":
            raise RuntimeError(f"linear pass failed: {custom_report['error']}")
    elif mode == "scheduled":
        from minicompiler.compiler.scheduled_matmul import run_scheduled_matmul
        from minicompiler.passes.redundant_reshape import run_redundant_reshape
        mod, reshape_report = run_redundant_reshape(mod)
        if reshape_report["status"] != "ok":
            raise RuntimeError(f"reshape pass failed: {reshape_report['error']}")
        mod, schedule_report = run_scheduled_matmul(mod, stage="vectorize")
        if schedule_report["status"] != "ok":
            raise RuntimeError(f"matmul schedule failed: {schedule_report['error']}")
        if not schedule_report["rewrites"]:
            raise ValueError("scheduled mode found no eligible matmul")
    main = mod["main"]
    attrs = main.attrs
    if attrs is not None and "params" in attrs and len(attrs["params"]):
        raise ValueError("artifact requires embedded model weights")
    if len(main.params) != len(summary["inputs"]):
        raise ValueError("model runtime input count differs from Relax function")
    executable, compile_ms, pipeline = compile_module(mod, target=target, mode="default" if mode == "scheduled" else mode)
    if mode == "scheduled":
        pipeline["mode"] = "scheduled"
        pipeline["schedule"] = "vectorize"
        pipeline["note"] = "reshape pass then matmul replaced by scheduled TIR before unchanged TVM default compilation"
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".artifact-", dir=output_dir.parent) as tmp:
        staged = Path(tmp)
        library = staged / "module.so"
        executable.export_library(str(library))
        manifest = {
            "format_version": 1,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime": {"tvm_version": tvm.__version__, "system": platform.system(),
                        "machine": platform.machine(), "target": target},
            "model": {"name": model_path.name, "onnx_file_sha256": _sha256(model_path),
                      "onnx_file_hash_scope": "main file only; external data not included",
                      "loaded_model_sha256": hashlib.sha256(model.SerializeToString(deterministic=True)).hexdigest(),
                      "weights": "embedded", "inputs": summary["inputs"], "outputs": summary["outputs"],
                      "opsets": summary["opsets"]},
            "executable": {"file": "module.so", "sha256": _sha256(library), "size_bytes": library.stat().st_size},
            "pipeline": pipeline, "compile_ms": compile_ms, "custom_pass": custom_report,
            "reshape_pass": reshape_report, "schedule": schedule_report,
        }
        (staged / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        # Reserve the destination exclusively before publishing either file.
        # A failure during publication may leave an incomplete directory, which
        # the loader rejects; an existing destination is never overwritten.
        output_dir.mkdir()
        os.rename(library, output_dir / "module.so")
        os.rename(staged / "manifest.json", output_dir / "manifest.json")
    return manifest


class LoadedArtifact:
    """An already-loaded CPU VM with named, shape-checked runtime inputs."""

    def __init__(self, module, manifest):
        self.manifest = manifest
        self._runner = TVMRunner(module, [item["name"] for item in manifest["model"]["inputs"]],
                                 manifest["compile_ms"], manifest["pipeline"])

    def run(self, inputs):
        expected = self.manifest["model"]["inputs"]
        if set(inputs) != {item["name"] for item in expected}:
            raise ValueError("input names do not match artifact manifest")
        for item in expected:
            array = np.asarray(inputs[item["name"]])
            if list(array.shape) != item["shape"] or str(array.dtype) != item["dtype"]:
                raise ValueError(f"input {item['name']!r} shape or dtype does not match artifact manifest")
        return self._runner.outputs_to_numpy(self._runner.run_prepared(self._runner.prepare_inputs(inputs)))


def load_artifact(output_dir):
    """Verify manifest and native library then load for the current CPU host."""
    directory = Path(output_dir)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("format_version") != 1:
        raise ValueError("unsupported artifact format")
    runtime = manifest["runtime"]
    if (runtime["tvm_version"] != tvm.__version__ or runtime["system"] != platform.system()
            or runtime["machine"] != platform.machine() or runtime["target"] != "llvm"):
        raise ValueError("artifact runtime version or platform does not match this host")
    executable = manifest["executable"]
    if executable["file"] != "module.so":
        raise ValueError("unexpected executable path")
    library = directory / "module.so"
    if _sha256(library) != executable["sha256"] or library.stat().st_size != executable["size_bytes"]:
        raise ValueError("artifact library does not match manifest")
    module = tvm.runtime.load_module(str(library))
    return LoadedArtifact(module, manifest)
