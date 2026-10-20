"""Adapt the installed workflow initializer to HCUP's worktree-at-task-root layout."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--project", required=True, type=Path)
parser.add_argument("--package", required=True, type=Path)
args = parser.parse_args()
root = args.project.resolve()
package = args.package.resolve()
skill = Path(r"C:\Users\22580\.codex\skills\harmony-task-flow")
workflow_script = skill / "scripts/workflow.py"
spec = package / "specs" / (args.task + ".md")
metadata_path = package / "metadata" / (args.task + ".json")
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))


def git(*command):
    return subprocess.check_output(["git", "-C", str(root), *command], encoding="utf-8").strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
    raise SystemExit("The destination must be the worktree root.")
if git("rev-parse", "HEAD") != metadata["base_commit"]:
    raise SystemExit("The worktree is not at this task's official base_commit.")
if (root / "workflow/state.json").exists():
    raise SystemExit("Workflow state already exists; inspect and resume instead of reinitializing.")
for name in ("inputs", "workflow", "traces", "system-config", "spec"):
    if (root / name).exists():
        raise SystemExit("Refusing to overwrite an existing preparation directory: " + name)

# The upstream initializer requires an empty root. Initialize in temporary storage,
# then explicitly adopt its records into the already verified Git worktree.
with tempfile.TemporaryDirectory(prefix=args.task + "-workflow-", dir=os.environ["TEMP"]) as temporary:
    temporary_parent = Path(os.environ["TEMP"]).resolve()
    temporary_path = Path(temporary).resolve()
    if temporary_path == temporary_parent or not temporary_path.is_relative_to(temporary_parent):
        raise SystemExit("Temporary initialization directory is outside the configured temporary root.")
    staging = Path(temporary) / "task"
    result = subprocess.run(
        [sys.executable, str(workflow_script), "init", "--task", args.task,
         "--root", str(staging), "--spec", str(spec), "--metadata", str(metadata_path)],
        check=True, capture_output=True, encoding="utf-8",
    )
    initial_state = json.loads((staging / "workflow/state.json").read_text(encoding="utf-8"))
    for name in ("inputs", "workflow", "traces", "system-config"):
        shutil.copytree(staging / name, root / name)
    guidance = (staging / "AGENTS.md").read_text(encoding="utf-8")
    guidance = guidance.replace(staging.as_posix(), root.as_posix())
    initial_state["root"] = str(root)
    initial_state["project"] = str(root)
    initial_state["layout"] = "HCUP: the task root is the Git worktree and project root"
    initial_state["next_action"] = "Verify the prepared baseline build; then open a dedicated task chat."
    for session in initial_state["sessions"]:
        session["purpose"] = "Initialization only; this overview conversation also contains environment setup and other task preparation. Not feature-development evidence."
    snapshot = root / initial_state["config_snapshot"]
    baseline_agents = root / "AGENTS.md"
    if baseline_agents.exists():
        shutil.copy2(baseline_agents, snapshot / "baseline-AGENTS.md")
        original = baseline_agents.read_text(encoding="utf-8")
    else:
        original = ""
    additions = (
        "\n\n---\n\n" + guidance +
        "\n## HCUP 工作区布局与阶段\n\n"
        "本题工程根就是当前目录；workflow/state.json 的 project 指向当前目录，"
        "不要再创建 project 子目录，也不要使用 Skill 示例中的另一套工程路径。\n\n"
        "本题需求读取 spec/requirement.md，元数据读取 spec/metadata.json；"
        "inputs/ 保留原始输入副本。公共资源只读访问 ../common/，不得访问其他赛题目录。\n\n"
        "开始构建或设备命令前加载 D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1。\n\n"
        "本次仅完成独立工程准备；尚未分析需求、设计方案或实现功能。"
        "正式作答从本目录的新会话开始，登记新会话后再按四角色流程推进。\n\n"
        "初始化总览会话也包含公共环境、官方示例与其他题的工程准备内容，不能将其视为本题功能开发证据；"
        "后续需求和编码角色不要读取该总览会话作为实现参考。\n"
    )
    baseline_agents.write_text(original.rstrip() + additions, encoding="utf-8")
    (root / "spec").mkdir()
    shutil.copy2(spec, root / "spec/requirement.md")
    shutil.copy2(metadata_path, root / "spec/metadata.json")
    template = root.parent / "common/spec-harness/submit-input.template.yaml"
    task_input = template.read_text(encoding="utf-8").replace('task_id: ""', f'task_id: "{args.task}"', 1)
    (root / "spec/submit-input.yaml").write_text(task_input, encoding="utf-8")
    for source in (root.parent / ".hcup-local/Enter-HarmonyEnv.ps1",
                   Path(r"D:\hongmengcup\Enter-HarmonyEnv.ps1")):
        environment_snapshot = snapshot / "environment"
        environment_snapshot.mkdir(exist_ok=True)
        prefix = "workspace-" if source.parent.name == ".hcup-local" else "toolchain-"
        shutil.copy2(source, environment_snapshot / (prefix + source.name))
    manifest = json.loads((package / "release-manifest.json").read_text(encoding="utf-8"))
    relevant = {"specs/" + args.task + ".md", "metadata/" + args.task + ".json", metadata["baseline_bundle"]}
    provenance = {
        "task_id": args.task, "package_commit": subprocess.check_output(
            ["git", "-C", str(package), "rev-parse", "HEAD"], encoding="utf-8").strip(),
        "official_base_commit": metadata["base_commit"], "local_base_tag": git("rev-parse", "base/" + args.task),
        "branch": git("branch", "--show-current"),
        "official_manifest_entries": [entry for entry in manifest["files"] if entry["path"] in relevant],
        "input_verification": {str(spec.relative_to(package)): sha256(spec),
                               str(metadata_path.relative_to(package)): sha256(metadata_path)},
        "note": "The local branch and base tag match official metadata. No extra baseline bundle download was needed.",
    }
    (root / "workflow/baseline-provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    module_spec = importlib.util.spec_from_file_location("hcup_workflow", workflow_script)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    module.append_event(root, initial_state, {
        "type": "adopt_verified_worktree", "original_layout": "initializer root with project subdirectory",
        "actual_layout": initial_state["layout"], "project": str(root),
        "base_commit": metadata["base_commit"], "source_initializer_result": json.loads(result.stdout),
        "reason": "Preserve the HCUP repository's existing per-task branch/worktree layout.",
    })
print(json.dumps({"task": args.task, "project": str(root), "state": str(root / "workflow/state.json")}, ensure_ascii=False))
