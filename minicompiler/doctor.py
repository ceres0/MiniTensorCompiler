"""Report the host and dependency status without requiring TVM to import."""

import importlib
import importlib.metadata
import os
import platform
import shutil
import subprocess
import sys


def _command(*args: str) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _cpu_model() -> str:
    if sys.platform == "darwin":
        return _command("sysctl", "-n", "machdep.cpu.brand_string") or platform.processor() or "unknown"
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                key, separator, value = line.partition(":")
                if separator and key.strip() in {"model name", "Hardware"}:
                    return value.strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def collect_report() -> dict:
    versions = {}
    for distribution in ("apache-tvm", "apache-tvm-ffi", "numpy", "onnx", "onnxruntime", "pytest"):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = None
    imports = {}
    for module in ("tvm", "tvm_tirx", "tvm.tirx", "tvm.relax"):
        try:
            importlib.import_module(module)
            imports[module] = "ok"
        except Exception as exc:
            imports[module] = f"{type(exc).__name__}: {exc}"
    llvm = _command("llvm-config", "--version") if shutil.which("llvm-config") else None
    tvm_llvm = None
    tvm_llvm_major = None
    if imports["tvm"] == "ok":
        try:
            import tvm
            tvm_llvm = tvm.support.libinfo().get("LLVM_VERSION")
            llvm_version = tvm.get_global_func("target.llvm_version_major", allow_missing=True)
            if llvm_version is not None:
                tvm_llvm_major = llvm_version()
        except (AttributeError, RuntimeError):
            pass
    return {
        "os": platform.platform(), "machine": platform.machine(), "cpu": _cpu_model(),
        "logical_cpu_count": os.cpu_count(), "python": platform.python_version(),
        "llvm_config_version": llvm, "tvm_build_llvm_version": tvm_llvm, "tvm_build_llvm_major": tvm_llvm_major,
        "packages": versions, "imports": imports,
    }
