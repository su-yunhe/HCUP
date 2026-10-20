"""Record hdc commands and device observations for vg-spec15 baseline only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
DEVICE = "127.0.0.1:5555"
HDC = shutil.which("hdc")
sys.stdout.reconfigure(encoding="utf-8")


def now():
    return datetime.now(timezone.utc).isoformat()


def event(kind, **data):
    row = {"time": now(), "kind": kind, **data}
    with (ROOT / "device-timeline.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False), flush=True)


def run(args, name=None, timeout=45):
    command = [HDC, "-t", DEVICE, *args]
    started = now()
    result = subprocess.run(command, capture_output=True, timeout=timeout)
    text = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    if name:
        (ROOT / (name + ".log")).write_text(text, encoding="utf-8")
    event("command", command=command, started=started, exit_code=result.returncode,
          output_file=(name + ".log") if name else None, output=text[:3000])
    if result.returncode != 0 or "[Fail]" in text or text.startswith("error:") or "ScreenCap failed" in text:
        raise RuntimeError(f"hdc exit {result.returncode}")
    return text


def snapshot(name):
    captured = []
    for command, extension in (("dumpLayout", "json"), ("screenCap", "png")):
        remote = f"/data/local/tmp/vg-spec15-{name}.{extension}"
        try:
            run(["shell", "uitest", command, "-p", remote], name + "-" + command)
            run(["file", "recv", remote, str(ROOT / (name + "." + extension))], name + "-recv-" + extension)
            captured.append(extension)
        except RuntimeError as error:
            event("capture_failed", name=name, extension=extension, error=str(error))
    event("snapshot", name=name, captured=captured)


def summarize(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    def visit(node):
        if isinstance(node, dict):
            attrs = node.get("attributes", {})
            if attrs:
                relevant = {key: attrs.get(key) for key in ("type", "text", "id", "enabled", "bounds", "bundleName")}
                if attrs.get("text") or attrs.get("type") in ("TextInput", "LoadingProgress", "Toggle", "Scroll"):
                    print(json.dumps(relevant, ensure_ascii=False))
            for child in node.get("children", []):
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
    visit(data)


def tap_text(text, name, expected_type=None):
    previous = None
    for attempt in range(1, 4):
        remote = f"/data/local/tmp/vg-spec15-{name}-locate-{attempt}.json"
        local = ROOT / f"{name}-locate-{attempt}.json"
        run(["shell", "uitest", "dumpLayout", "-p", remote], f"{name}-locate-{attempt}")
        run(["file", "recv", remote, str(local)], f"{name}-recv-{attempt}")
        candidates = []
        def visit(node):
            if isinstance(node, dict):
                attrs = node.get("attributes", {})
                if (attrs.get("text") == text and attrs.get("visible") == "true"
                        and (expected_type is None or attrs.get("type") == expected_type)):
                    candidates.append(attrs)
                for child in node.get("children", []):
                    visit(child)
            elif isinstance(node, list):
                for child in node:
                    visit(child)
        visit(json.loads(local.read_text(encoding="utf-8")))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one visible {text!r}, got {len(candidates)}")
        bounds = candidates[0]["bounds"]
        if bounds == previous:
            left, top, right, bottom = [int(value) for value in re.findall(r"-?\d+", bounds)]
            event("tap_text", text=text, type=candidates[0]["type"], bounds=bounds,
                  evidence=local.name, stable_observations=attempt)
            run(["shell", "uitest", "uiInput", "click", str((left+right)//2), str((top+bottom)//2)], name)
            return
        previous = bounds
    raise RuntimeError(f"Bounds did not stabilize for {text!r}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["run", "snapshot", "summary", "note", "tap_text"])
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    parser.add_argument("--name")
    options = parser.parse_args()
    if options.operation == "run":
        run(options.arguments, options.name)
    elif options.operation == "snapshot":
        snapshot(options.arguments[0])
        summarize(ROOT / (options.arguments[0] + ".json"))
    elif options.operation == "summary":
        summarize(ROOT / (options.arguments[0] + ".json"))
    elif options.operation == "tap_text":
        tap_text(options.arguments[0], options.arguments[1], options.arguments[2] if len(options.arguments) > 2 else None)
    else:
        event("note", detail=" ".join(options.arguments))
