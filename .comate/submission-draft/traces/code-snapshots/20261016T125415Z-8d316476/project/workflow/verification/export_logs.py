"""Place final valid reports and explicit historical references under logs/."""
import collections
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
traces = root / "traces/implementation-validation"
logs = root / "logs"
logs.mkdir(exist_ok=True)
runs = sys.argv[1:]
merged = {}
reports = []
install_sections = []
selftest_sections = []
for name in runs:
    folder = traces / name
    report = json.loads((folder / "selftest.json").read_text(encoding="utf-8"))
    for case in report["cases"]:
        merged[case["name"]] = {**case, "evidence_run": name,
                                "raw_report": (folder / "selftest.json").relative_to(root).as_posix()}
    reports.append({"run": name, "runner_exit": int((folder / "selftest-exit.txt").read_text().strip()),
                    "report": (folder / "selftest.json").relative_to(root).as_posix(),
                    "raw_log": (folder / "selftest-raw.log").relative_to(root).as_posix()})
    command = (folder / "Run-command.log").read_text(encoding="utf-8-sig")
    start = command.index("COMMAND: hdc ")
    end = command.index("COMMAND: D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner")
    install_sections.append(f"RUN {name}\nSOURCE {folder.relative_to(root)}/Run-command.log\n" + command[start:end])
    selftest_sections.append(f"RUN {name}\nSOURCE {folder.relative_to(root)}/selftest-raw.log\n" +
                             (folder / "selftest-raw.log").read_text(encoding="utf-8-sig"))
valid_cases = [merged[name] for name in sorted(merged)]
out = {"project": str(root), "device_sn": "127.0.0.1:5555", "cases": valid_cases,
       "counts": dict(collections.Counter(case["outcome"] for case in valid_cases)),
       "raw_runs": reports,
       "failure_history": [{"run": "round02-t1", "classification": "test harness lowercase swipe direction before sync click",
                            "report": "traces/implementation-validation/round02-t1/selftest.json"}],
       "official_result": "not_available"}
(logs / "build.log").write_bytes((traces / "round02-t1/build-raw.log").read_bytes())
(logs / "install.log").write_text("\n\n".join(install_sections), encoding="utf-8")
(logs / "selftest.log").write_text("\n\n".join(selftest_sections), encoding="utf-8")
(logs / "selftest.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
manifest = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
            for file in (logs / "build.log", logs / "install.log", logs / "selftest.log", logs / "selftest.json")}
(logs / "verification-log-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"counts": out["counts"], "raw_runs": reports, "log_manifest": manifest}, indent=2))
