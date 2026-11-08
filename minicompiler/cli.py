"""Command-line entry point."""
import argparse
import json
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
    args = parser.parse_args(argv)
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
