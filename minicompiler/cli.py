"""Command-line entry point."""
import argparse
import json
import os
from pathlib import Path
import sys

from .doctor import collect_report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="minicompiler")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="report environment and dependency availability")
    importer = subparsers.add_parser("import", help="validate ONNX and inspect the imported Relax IR")
    importer.add_argument("--model", required=True, type=Path, help="input ONNX model")
    importer.add_argument("--output-dir", required=True, type=Path, help="directory for summary and IR dumps")
    importer.add_argument("--keep-params-in-input", action="store_true", help="retain weights as Relax function parameters")
    reshape = subparsers.add_parser("reshape", help="run the redundant reshape pass on an ONNX model")
    reshape.add_argument("--model", required=True, type=Path)
    reshape.add_argument("--output-dir", required=True, type=Path)
    reshape.add_argument("--disable", action="store_true", help="dump unchanged IR for comparison")
    linear = subparsers.add_parser("linear", help="group guarded MatMul + bias + ReLU subgraphs")
    linear.add_argument("--model", required=True, type=Path)
    linear.add_argument("--output-dir", required=True, type=Path)
    linear.add_argument("--disable", action="store_true")
    linear.add_argument("--keep-params-in-input", action="store_true")
    evidence = subparsers.add_parser("evidence", help="capture an ONNX-to-LLVM CPU evidence chain")
    evidence.add_argument("--model", required=True, type=Path)
    evidence.add_argument("--output-dir", required=True, type=Path)
    evidence.add_argument("--pass-mode", choices=["none", "reshape", "linear", "scheduled"], default="linear")
    compile_cmd = subparsers.add_parser("compile", help="compile and export a CPU VM artifact")
    compile_cmd.add_argument("--model", required=True, type=Path)
    compile_cmd.add_argument("--target", choices=["llvm"], default="llvm")
    compile_cmd.add_argument("--mode", choices=["default", "nofusion", "custom", "scheduled"], default="default")
    compile_cmd.add_argument("--output", required=True, type=Path)
    run_cmd = subparsers.add_parser("run", help="run an exported CPU VM artifact on NPZ inputs")
    run_cmd.add_argument("--artifact", required=True, type=Path)
    run_cmd.add_argument("--inputs", required=True, type=Path)
    run_cmd.add_argument("--output", required=True, type=Path)
    bench = subparsers.add_parser("bench", help="compare a TVM CPU baseline with ONNX Runtime")
    bench.add_argument("--model", type=Path, required=True)
    bench.add_argument("--target", choices=["llvm"], default="llvm")
    bench.add_argument("--mode", choices=["default", "nofusion", "custom"], default="default")
    bench.add_argument("--threads", type=int, default=1)
    bench.add_argument("--seed", type=int, default=0)
    bench.add_argument("--warmup", type=int, default=30)
    bench.add_argument("--repeat", type=int, default=100)
    bench.add_argument("--rounds", type=int, default=3)
    bench.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "evidence":
        from .compiler.evidence import export_evidence
        try:
            export_evidence(args.model, args.output_dir, pass_mode=args.pass_mode)
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"Evidence export failed: {exc}", file=sys.stderr)
            return 1
        print(f"Evidence written to {args.output_dir}")
        return 0
    if args.command == "compile":
        from .compiler.artifacts import export_onnx_artifact
        try:
            export_onnx_artifact(args.model, args.output, target=args.target, mode=args.mode)
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"Compilation failed: {exc}", file=sys.stderr)
            return 1
        print(f"VM artifact written to {args.output}")
        return 0
    if args.command == "run":
        import numpy as np
        from .compiler.artifacts import load_artifact
        try:
            if args.output.exists():
                raise FileExistsError(f"output already exists: {args.output}")
            artifact = load_artifact(args.artifact)
            with np.load(args.inputs, allow_pickle=False) as archive:
                inputs = {key: archive[key] for key in archive.files}
            values = artifact.run(inputs)
            names = artifact.manifest["model"]["outputs"]
            if len(names) != len(values) or len(set(names)) != len(names):
                raise ValueError("artifact output names do not match VM outputs")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as file:
                np.savez(file, **dict(zip(names, values, strict=True)))
        except (ValueError, RuntimeError, OSError, KeyError) as exc:
            print(f"VM execution failed: {exc}", file=sys.stderr)
            return 1
        print(f"VM outputs written to {args.output}")
        return 0
    if args.command == "linear":
        from .frontend.onnx_loader import OnnxImportError, import_relax, load_and_summarize
        from .passes.linear_bias_relu import run_linear_bias_relu
        try:
            names = ("00_relax_before.py", "01_relax_after.py", "02_linear_report.json")
            if any((args.output_dir / name).exists() for name in names):
                raise FileExistsError(f"output files already exist in {args.output_dir}; choose a new directory")
            model, _ = load_and_summarize(args.model)
            before = import_relax(model, keep_params_in_input=args.keep_params_in_input)
            after, report = run_linear_bias_relu(before, enabled=not args.disable)
            report["keep_params_in_input"] = args.keep_params_in_input
            before_text, after_text = before.script(), after.script()
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / names[0]).write_text(before_text + "\n", encoding="utf-8")
            (args.output_dir / names[1]).write_text(after_text + "\n", encoding="utf-8")
            (args.output_dir / names[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except (OnnxImportError, ValueError, RuntimeError, OSError) as exc:
            print(f"Linear pass failed: {exc}", file=sys.stderr)
            return 1
        print(f"Linear pass report and IR written to {args.output_dir}")
        if report.get("status") == "failed":
            print(f"Linear pass rolled back: {report.get('error')}", file=sys.stderr)
            return 1
        return 0
    if args.command == "reshape":
        from .frontend.onnx_loader import OnnxImportError, import_relax, load_and_summarize
        from .passes.redundant_reshape import run_redundant_reshape
        try:
            names = ("00_relax_before.py", "01_relax_after.py", "02_reshape_report.json")
            if any((args.output_dir / name).exists() for name in names):
                raise FileExistsError(f"output files already exist in {args.output_dir}; choose a new directory")
            model, _ = load_and_summarize(args.model)
            before = import_relax(model, keep_params_in_input=False)
            after, report = run_redundant_reshape(before, enabled=not args.disable)
            before_text, after_text = before.script(), after.script()
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / names[0]).write_text(before_text + "\n", encoding="utf-8")
            (args.output_dir / names[1]).write_text(after_text + "\n", encoding="utf-8")
            (args.output_dir / names[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except (OnnxImportError, ValueError, RuntimeError, OSError) as exc:
            print(f"Reshape pass failed: {exc}", file=sys.stderr)
            return 1
        print(f"Reshape pass report and IR written to {args.output_dir}")
        if report.get("status") == "failed":
            print(f"Reshape pass rolled back: {report.get('error')}", file=sys.stderr)
            return 1
        return 0
    if args.command == "bench":
        if args.threads < 1 or args.seed < 0 or args.warmup < 0 or args.repeat < 1 or args.rounds < 1:
            parser.error("threads, repeat and rounds must be positive; seed and warmup must be nonnegative")
        # Set thread limits before importing TVM, ORT or NumPy in this process.
        os.environ["TVM_NUM_THREADS"] = str(args.threads)
        os.environ["OMP_NUM_THREADS"] = str(args.threads)
        os.environ["OPENBLAS_NUM_THREADS"] = str(args.threads)
        from .profiling.report import run_benchmark
        try:
            if args.output and args.output.exists():
                raise FileExistsError(f"output already exists: {args.output}; choose a new path")
            report = run_benchmark(args.model, target=args.target, mode=args.mode,
                                   threads=args.threads, seed=args.seed, warmup=args.warmup,
                                   repeat=args.repeat, rounds=args.rounds)
            text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(text, encoding="utf-8")
                print(f"Benchmark report written to {args.output}")
            else:
                print(text, end="")
            return 0 if report["correctness"]["passed"] else 1
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"Benchmark failed: {exc}", file=sys.stderr)
            return 1
    if args.command == "doctor":
        report = collect_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        required = ("tvm", "tvm.tirx", "tvm.relax")
        return 0 if all(report["imports"][name] == "ok" for name in required) else 1
    if args.command == "import":
        from .frontend.onnx_loader import OnnxImportError, import_relax, load_and_summarize
        from .ir.inspector import UnknownShapeError, inspect_module

        try:
            output_names = ("00_onnx_summary.json", "01_relax_imported.py", "02_relax_inspection.json")
            if any((args.output_dir / name).exists() for name in output_names):
                raise FileExistsError(f"output files already exist in {args.output_dir}; choose a new directory")
            model, summary = load_and_summarize(args.model)
            module = import_relax(model, keep_params_in_input=args.keep_params_in_input)
            inspection = inspect_module(module)
            summary["keep_params_in_input"] = args.keep_params_in_input
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / "00_onnx_summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            (args.output_dir / "01_relax_imported.py").write_text(module.script() + "\n", encoding="utf-8")
            (args.output_dir / "02_relax_inspection.json").write_text(
                json.dumps(inspection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except (OnnxImportError, UnknownShapeError, OSError) as exc:
            print(f"Import failed: {exc}", file=sys.stderr)
            return 1
        print(f"ONNX summary and Relax IR written to {args.output_dir}")
        return 0
