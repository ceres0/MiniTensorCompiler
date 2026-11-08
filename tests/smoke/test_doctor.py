import json
import subprocess
import sys

from minicompiler.doctor import collect_report


def test_doctor_reports_host_and_required_imports():
    report = collect_report()
    assert report["os"] and report["cpu"] and report["logical_cpu_count"]
    assert set(report["imports"]) == {"tvm", "tvm_tirx", "tvm.tirx", "tvm.relax"}
    assert report["packages"]["apache-tvm"] == "0.27.0.post1"
    assert all(report["imports"][name] == "ok" for name in ("tvm", "tvm.tirx", "tvm.relax"))


def test_doctor_cli_emits_json():
    result = subprocess.run([sys.executable, "-m", "minicompiler", "doctor"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["packages"]["apache-tvm"] == "0.27.0.post1"
