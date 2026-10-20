"""Retain final source comparison, generated file inventory, and environment outputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
logs = root / "logs/analysis-baseline"
manifests = {name: json.loads((logs / f"fingerprint-{name}.json").read_text(encoding="utf-8"))
             for name in ["before", "after-build", "final"]}
baseline = {row["path"]: row for row in manifests["before"]["inputs"]}
diffs = {}
for name in ["after-build", "final"]:
    current = {row["path"]: row for row in manifests[name]["inputs"]}
    diffs[name] = [{"path": path, "before": baseline.get(path), "after": current.get(path)}
                   for path in sorted(baseline.keys() | current.keys()) if baseline.get(path) != current.get(path)]
start = datetime.fromisoformat(manifests["before"]["timestamp_utc"]).timestamp()
generated = []
for directory, subdirs, files in os.walk(root):
    subdirs[:] = [item for item in subdirs if item not in {".git", "oh_modules", "inputs", "system-config", "logs", "traces", "workflow", "test-harness", "spec-harness"}]
    for filename in files:
        path = Path(directory) / filename
        relative = path.relative_to(root)
        if ("build" in relative.parts or ".hvigor" in relative.parts or filename == "BuildProfile.ets") and path.stat().st_mtime >= start:
            generated.append({"path": relative.as_posix(), "bytes": path.stat().st_size})
hap = root / "entry/build/default/outputs/default/entry-default-unsigned.hap"
result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "head": manifests["final"]["head"],
          "source_count": len(baseline), "source_comparison": diffs,
          "tracked_diff": subprocess.check_output(["git", "diff", "--name-status"], cwd=root).decode(),
          "tracked_staged_diff": subprocess.check_output(["git", "diff", "--cached", "--name-status"], cwd=root).decode(),
          "hap": {"path": hap.relative_to(root).as_posix(), "bytes": hap.stat().st_size,
                  "sha256": hashlib.sha256(hap.read_bytes()).hexdigest()},
          "spec_sha256": hashlib.sha256((root / "spec/requirement.md").read_bytes()).hexdigest(),
          "requirements_draft_sha256": hashlib.sha256((root / "workflow/requirements/acceptance-draft.md").read_bytes()).hexdigest(),
          "generated_files": generated}
(logs / "closeout.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile("D:/HarmonyDev/emulator/instances/HarmonyCup_API23/config.ini", logs / "emulator-config.ini")
environment = dict(os.environ, PYTHONPATH=str(root / "test-harness"), PYTHONDONTWRITEBYTECODE="1")
command = [sys.executable, "-m", "harness.env_check", "--device", "127.0.0.1:5555"]
check = subprocess.run(command, cwd=root, env=environment, capture_output=True)
env_result = {"command": command, "exit_code": check.returncode,
              "stdout": check.stdout.decode("utf-8", errors="replace"), "stderr": check.stderr.decode("utf-8", errors="replace")}
(logs / "env-check-final.json").write_text(json.dumps(env_result, ensure_ascii=False, indent=2), encoding="utf-8")
(logs / "env-check-final.stdout.txt").write_bytes(check.stdout)
(logs / "env-check-final.stderr.txt").write_bytes(check.stderr)
print(json.dumps({key: value for key, value in result.items() if key != "generated_files"}, ensure_ascii=False, indent=2))
print(f"Generated output paths inventoried: {len(generated)}")
print(f"Final environment check exit={check.returncode}")
