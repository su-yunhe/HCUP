"""Analysis-only baseline device operations; no application source modifications."""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "traces/baseline-analysis/r3"
LOGS = ROOT / "logs"
DEVICE = "127.0.0.1:11245"


def run(label: str, args: list[str]) -> dict:
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(["hdc", "-t", DEVICE, *args], cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding="utf-8", errors="replace", timeout=45)
    record = {"label": label, "utc": started, "args": ["hdc", "-t", DEVICE, *args],
              "exit_code": result.returncode, "output": result.stdout,
              "output_has_failure": "[Fail]" in result.stdout}
    (LOGS / f"analysis-baseline-r3-{label}.log").write_text(result.stdout, encoding="utf-8")
    with (LOGS / "analysis-baseline-r3-probe-commands.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    if result.returncode != 0 or record["output_has_failure"]:
        raise RuntimeError(json.dumps(record, ensure_ascii=False))
    print(json.dumps({"label": label, "exit_code": result.returncode,
                      "utc": started, "output_chars": len(result.stdout)}, ensure_ascii=False), flush=True)
    return record


def screen(label: str) -> None:
    remote = f"/data/local/tmp/cml-spec1-r3-{label}.png"
    run(label + "-screen", ["shell", "uitest", "screenCap", "-p", remote])
    run(label + "-screen-recv", ["file", "recv", remote, str(pathlib.Path("traces/baseline-analysis/r3") / f"{label}.png")])


def capture(label: str) -> None:
    # Bracket the dump with two screenshots after the caller's settled-state wait.
    screen(label)
    remote = f"/data/local/tmp/cml-spec1-r3-{label}.json"
    run(label + "-dump", ["shell", "uitest", "dumpLayout", "-a", "-p", remote])
    run(label + "-dump-recv", ["file", "recv", remote, str(pathlib.Path("traces/baseline-analysis/r3") / f"{label}.json")])
    screen(label + "-after")
    tree = json.loads((OUT / f"{label}.json").read_text(encoding="utf-8-sig"))
    rows = []

    def walk(node: dict) -> None:
        attrs = node.get("attributes", {})
        if attrs.get("text") or attrs.get("type") in ("Tabs", "TabContent", "Scroll", "List"):
            rows.append({key: attrs.get(key) for key in
                         ("text", "type", "id", "key", "bounds", "visible", "selected", "clickable")})
        for child in node.get("children", []):
            walk(child)

    walk(tree)
    (OUT / f"{label}-nodes.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"capture": label, "nodes": rows}, ensure_ascii=False), flush=True)


parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["capture", "click", "swipe", "restart"])
parser.add_argument("label")
parser.add_argument("values", nargs="*")
options = parser.parse_args()
if options.action == "click":
    run(options.label + "-click", ["shell", "uitest", "uiInput", "click", *options.values])
    time.sleep(1.5)
elif options.action == "swipe":
    run(options.label + "-swipe", ["shell", "uitest", "uiInput", "swipe", *options.values])
    time.sleep(1.5)
elif options.action == "restart":
    run(options.label + "-stop", ["shell", "aa", "force-stop", "com.joker.coolmall"])
    run(options.label + "-launch", ["shell", "aa", "start", "-a", "EntryAbility", "-b", "com.joker.coolmall"])
    time.sleep(4)
capture(options.label)
