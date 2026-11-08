"""Command-line entry point."""
import argparse
import json

from .doctor import collect_report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="minicompiler")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="report environment and dependency availability")
    args = parser.parse_args(argv)
    if args.command == "doctor":
        report = collect_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        required = ("tvm", "tvm.tirx", "tvm.relax")
        return 0 if all(report["imports"][name] == "ok" for name in required) else 1
