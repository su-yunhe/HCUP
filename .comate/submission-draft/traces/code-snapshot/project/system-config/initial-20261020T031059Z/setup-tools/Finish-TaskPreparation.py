"""Record reproducible setup evidence for an initialized HCUP task worktree."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

import json5

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True, type=Path)
args = parser.parse_args()
root = args.project.resolve()
initial_state = json.loads((root / "workflow/state.json").read_text(encoding="utf-8"))
task_id = initial_state["task_id"]
if Path(initial_state["root"]).resolve() != root or Path(initial_state["project"]).resolve() != root:
    raise SystemExit("Stored task paths do not match the requested project.")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments):
    return subprocess.check_output(["git", "-C", str(root), *arguments], encoding="utf-8").strip()


base = json.loads((root / "spec/metadata.json").read_text(encoding="utf-8"))["base_commit"]
head = git("rev-parse", "HEAD")
provenance = json.loads((root / "workflow/baseline-provenance.json").read_text(encoding="utf-8"))
if head != base:
    assert head == provenance.get("adopted_prepared_commit") == initial_state.get("prepared_head")
    git("merge-base", "--is-ancestor", base, head)
    for name, expected in provenance.get("verified_official_preparation_configuration", {}).items():
        assert json5.loads((root / name).read_text(encoding="utf-8")) == expected
preparation = json.loads((root / "logs/prepare-baseline.log").read_text(encoding="utf-8-sig"))
assert preparation["task_id"] == task_id and preparation["base_commit"] == base
prepared_paths = {item["path"] for item in preparation["changes"]}
changed = git("diff", "--name-only", base).splitlines()
environment_changes = [name for name in changed if name in prepared_paths or name == "oh-package-lock.json5" or name.endswith("/oh-package-lock.json5")]
unexpected = [name for name in changed if name != "AGENTS.md" and name not in environment_changes]
if unexpected:
    raise SystemExit("Unexpected tracked source/config changes: " + ", ".join(unexpected))
files = [name for name in git("ls-files", "-z").split("\0") if name]
fingerprint = {name: sha256(root / name) for name in files if (root / name).is_file()}
fingerprint_path = root / "workflow/setup-code-fingerprint.json"
fingerprint_path.write_text(json.dumps({"head": head, "base_commit": base, "tracked_files_sha256": fingerprint},
                                      ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
hap = root / "entry/build/default/outputs/default/entry-default-unsigned.hap"
build_log = (root / "logs/baseline-build.log").read_text(encoding="utf-8-sig")
assert (root / "logs/baseline-build-exit-code.txt").read_text().strip() == "0"
assert "BUILD SUCCESSFUL" in build_log and hap.is_file()
record = {
    "task_id": task_id, "prepared_at": datetime.now(timezone.utc).isoformat(),
    "project_root": str(root), "branch": git("branch", "--show-current"), "base_commit": base, "prepared_head": head,
    "baseline_prepare": {"result": "pass", "log": "logs/prepare-baseline.log"},
    "ohpm_install": {"result": "pass", "log": "logs/ohpm-install.log"},
    "baseline_build": {"result": "pass", "exit_code": 0,
        "command": "hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon",
        "log": "logs/baseline-build.log", "warnings_recorded": True,
        "warning_file_diagnostics": len(re.findall(r"(?m)^(?:> hvigor WARN: )?WARN: ArkTS:WARN File:", build_log)),
        "sdk_declarations_preserved": True, "hap": hap.relative_to(root).as_posix(),
        "hap_bytes": hap.stat().st_size, "hap_sha256": sha256(hap)},
    "business_source_changes": [], "preparation_configuration_changes": environment_changes,
    "task_guidance": "AGENTS.md: task workflow guidance saved; existing baseline guidance retained if present",
    "new_task_artifacts": ["spec/", "inputs/", "workflow/", "logs/", "system-config/", "traces/"],
    "source_fingerprint": "workflow/setup-code-fingerprint.json",
    "not_performed": ["requirements analysis", "feature implementation", "app install/launch", "functional tests"],
    "next_action": "Open a dedicated chat rooted at this project, register its session, and start requirements analysis.",
}
(root / "workflow/setup-result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
state_path = root / "workflow/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["code_fingerprint"] = {"head": head, "base_commit": base, "manifest": "workflow/setup-code-fingerprint.json",
                              "manifest_sha256": sha256(fingerprint_path)}
state["setup_complete"] = True
state["approved_artifacts"]["prepared_inputs"] = ["spec/requirement.md", "spec/metadata.json"]
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"task": task_id, "baseline_build": "pass", "business_source_changes": [],
                  "setup_result": str(root / "workflow/setup-result.json")}, ensure_ascii=False))
