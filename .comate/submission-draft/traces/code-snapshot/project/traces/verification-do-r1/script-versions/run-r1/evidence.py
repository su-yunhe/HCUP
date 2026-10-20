"""Auditable device commands, source fingerprints, trees and real screen frames.

No command runs at import time. The public runner supplies the target device.
The screenshot worker uses an independent shell, not concurrent UiDriver calls.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from hypium import BY

ROOT = Path(__file__).resolve().parents[1]
KEYS = ("home", "category", "cart", "me")
LABELS = ("首页", "分类", "购物车", "我的")


class ObservationUnavailable(RuntimeError):
    """A required observation was blocked by the collection tool, not a product verdict."""


def save_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def source_manifest():
    tracked = subprocess.check_output(["git", "ls-files", "--cached"], cwd=ROOT, text=True).splitlines()
    new = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "entry", "core", "feature", "hvigor"],
        cwd=ROOT, text=True).splitlines()
    result = {}
    for name in sorted(set(tracked + new)):
        if re.search(r"(^|/)(build|oh_modules|\.hvigor)/", name):
            continue
        p = ROOT / name
        if p.is_file():
            result[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def rectangle(value):
    if hasattr(value, "left"):
        return [int(value.left), int(value.top), int(value.right), int(value.bottom)]
    parts = [int(x) for x in re.findall(r"-?\d+", str(value))]
    if len(parts) != 4:
        raise AssertionError(f"Cannot parse bounds: {value!r}")
    return parts


def intersection(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def area(a):
    return max(0, a[2] - a[0]) * max(0, a[3] - a[1])


def flatten_tree(tree):
    found = {}

    def walk(node):
        if isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            attrs = node.get("attributes", {})
            key = attrs.get("key") or attrs.get("id")
            if key:
                found.setdefault(key, []).append({"attributes": attrs, "extraAttrs": node.get("extraAttrs", {})})
            for key, child in node.items():
                if key not in ("attributes", "extraAttrs"):
                    walk(child)

    walk(tree)
    return found


class Evidence:
    def __init__(self, case, serial, run_dir):
        self.case, self.serial = case, serial
        self.path = Path(run_dir) / case._testMethodName
        self.path.mkdir(parents=True, exist_ok=True)
        self.remote = "/data/local/tmp/cml_spec1_verify_" + str(time.time_ns())
        self.command_log = self.path / "commands.jsonl"
        self.lock = threading.Lock()
        self.seq = 0
        self.observations = []
        self.states = []
        self.reference = source_manifest()
        save_json(self.path / "source-before.json", self.reference)
        self.cmd("shell", "mkdir", "-p", self.remote)

    def log(self, record):
        with self.lock:
            with self.command_log.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    def cmd(self, *args, timeout=40, check=True):
        argv = ["hdc", "-t", self.serial, *map(str, args)]
        start = time.monotonic()
        proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        self.log({"argv": argv, "started": start, "finished": time.monotonic(), "exit": proc.returncode,
                  "stdout": proc.stdout, "stderr": proc.stderr})
        if check and proc.returncode:
            raise AssertionError(f"Command failed ({proc.returncode}): {argv}: {proc.stdout} {proc.stderr}")
        return proc

    def component(self, ident, required=True):
        c = self.case.driver.find_component(BY.key(ident))
        if required and c is None:
            raise AssertionError(f"Required stable ID missing: {ident}")
        return c

    def state(self, ident, required=True):
        c = self.component(ident, required)
        if c is None:
            return None
        text = c.getDescription()
        if not text and not required:
            return None
        try:
            parsed = json.loads(text)
        except (ValueError, TypeError) as exc:
            raise ObservationUnavailable(f"Engine/state description unavailable for {ident}: {text!r}; compare source and XML before attribution") from exc
        return parsed

    def sample(self, all_icons=False):
        record = {"time": time.monotonic()}
        root = self.state("main_root", required=False)
        if root is not None:
            record["root"] = root
            current = int(root["selectedIndex"])
            observe = KEYS if all_icons else [KEYS[current], "home"]
            for key in dict.fromkeys(observe):
                state = self.state(f"main_tab_{key}_icon", required=False)
                if state is not None:
                    record[key] = state
        self.states.append(record)
        return record

    def tree(self, label):
        remote = f"{self.remote}/{label}.json"
        start = time.monotonic()
        self.cmd("shell", "uitest", "dumpLayout", "-a", "-p", remote)
        local = self.path / f"{label}.json"
        self.cmd("file", "recv", remote, local)
        raw = json.loads(local.read_text(encoding="utf-8-sig"))
        nodes = flatten_tree(raw)
        save_json(self.path / f"{label}-nodes.json", nodes)
        self.log({"tree": str(local), "started": start, "finished": time.monotonic()})
        return nodes

    def screenshot(self, label):
        remote = f"{self.remote}/{label}.png"
        local = self.path / f"{label}.png"
        self.cmd("shell", "uitest", "screenCap", "-p", remote)
        self.cmd("file", "recv", remote, local)
        if cv2.imread(str(local)) is None:
            raise AssertionError(f"Invalid screenshot {local}")
        return local

    def snapshot(self, label):
        nodes = self.tree(label)
        self.screenshot(label)
        self.sample(all_icons=True)
        save_json(self.path / "state-samples.json", self.states)
        return nodes

    @contextlib.contextmanager
    def check(self, *items, details=None):
        record = {"items": list(items), "started": time.monotonic(), "details": details}
        try:
            yield
        except BaseException as exc:
            record.update(status="blocked" if isinstance(exc, ObservationUnavailable) else "fail",
                          error=f"{type(exc).__name__}: {exc}")
            raise
        else:
            record["status"] = "pass"
        finally:
            record["finished"] = time.monotonic()
            self.observations.append(record)
            save_json(self.path / "a-observations.json", self.observations)

    def unchanged(self):
        after = source_manifest()
        save_json(self.path / "source-after.json", after)
        differences = sorted(name for name in set(self.reference) | set(after) if self.reference.get(name) != after.get(name))
        save_json(self.path / "source-difference.json", differences)
        if differences:
            raise AssertionError(f"Source changed during tests; invalidate evidence and remeasure: {differences}")


class FrameCapture:
    """Capture actual device images before/during/after one action.

    A single native-shell loop avoids PC transfer delays in the sampling loop.
    Original JPEG/PNG and device uptime plus host arrival times are retained.
    Backend is configurable only for tool compatibility, never to fake frames.
    """
    def __init__(self, evidence, label, count=48, interval=.1):
        self.e, self.label = evidence, label
        self.count = int(os.environ.get("CML_CAPTURE_FRAMES", count))
        self.interval = interval
        self.remote = f"{evidence.remote}/{label}"
        self.path = evidence.path / label
        self.path.mkdir(parents=True, exist_ok=True)
        self.rows = []
        self.ready = threading.Event()

    def start(self):
        backend = os.environ.get("CML_CAPTURE_BACKEND", "snapshot_display")
        if backend not in ("snapshot_display", "uitest"):
            raise ValueError(f"Unsupported capture backend: {backend}")
        shot = ('snapshot_display -f "$out"' if backend == "snapshot_display" else 'uitest screenCap -p "$out"')
        suffix = "jpeg" if backend == "snapshot_display" else "png"
        script = (f"mkdir -p {self.remote}; i=0; while [ $i -lt {self.count} ]; do "
                  "read stamp rest < /proc/uptime; echo FRAME_START $i $stamp; "
                  f'out={self.remote}/frame_$i.{suffix}; {shot}; rc=$?; '
                  "read stamp rest < /proc/uptime; echo FRAME_END $i $stamp $rc; "
                  f"i=$((i+1)); sleep {self.interval}; done")
        self.argv = ["hdc", "-t", self.e.serial, "shell", script]
        self.started = time.monotonic()
        self.proc = subprocess.Popen(self.argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding="utf-8", errors="replace")

        def read_output():
            with (self.path / "capture-raw.log").open("w", encoding="utf-8") as log:
                for line in self.proc.stdout:
                    log.write(line)
                    log.flush()
                    match = re.search(r"FRAME_(START|END) (\d+) ([\d.]+)(?: (\d+))?", line)
                    if match:
                        self.rows.append({"event": match[1], "index": int(match[2]), "deviceUptime": float(match[3]),
                                          "hostMonotonic": time.monotonic(), "exit": int(match[4]) if match[4] else None})
                        self.ready.set()

        self.reader = threading.Thread(target=read_output, daemon=True)
        self.reader.start()
        if not self.ready.wait(10):
            raise ObservationUnavailable("Native frame capture did not start; see capture-raw.log")
        if self.proc.poll() is not None:
            raise ObservationUnavailable("Frame shell output was buffered until completion; action has not run and evidence is invalid")
        return self

    def finish(self):
        try:
            code = self.proc.wait(timeout=90)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            self.proc.wait(timeout=10)
            raise ObservationUnavailable("Frame capture timed out; raw evidence retained")
        self.reader.join(timeout=5)
        self.e.log({"argv": self.argv, "started": self.started, "finished": time.monotonic(), "exit": code,
                    "raw": str(self.path / "capture-raw.log")})
        save_json(self.path / "frame-times.json", self.rows)
        if code:
            raise ObservationUnavailable(f"Frame capture shell failed: {code}")
        failed = [r for r in self.rows if r["event"] == "END" and r["exit"] != 0]
        if failed:
            raise ObservationUnavailable(f"Native screenshots failed; do not infer animation from diagnostics: {failed[:3]}")
        self.e.cmd("file", "recv", self.remote, str(self.path))
        # hdc implementations differ in whether recv(dir, existing_dir) nests the source basename.
        self.images = sorted(self.path.rglob("frame_*.*"), key=lambda p: int(re.search(r"frame_(\d+)", p.name)[1]))
        if len(self.images) != self.count:
            raise ObservationUnavailable(f"Expected {self.count} actual screen images, received {len(self.images)}")
        return self

    def roi(self, bounds, suffix, after=0):
        results = []
        starts = {r["index"]: r for r in self.rows if r["event"] == "START"}
        for path in self.images:
            index = int(re.search(r"frame_(\d+)", path.name)[1])
            if starts[index]["hostMonotonic"] < after:
                continue
            image = cv2.imread(str(path))
            if image is None:
                raise AssertionError(f"Invalid actual PNG {path}")
            left, top, right, bottom = bounds
            crop = image[top:bottom, left:right]
            if crop.size == 0:
                raise AssertionError(f"Empty ROI {bounds} in {path}")
            out = self.path / f"roi_{suffix}_{index}.png"
            cv2.imwrite(str(out), crop)
            results.append((starts[index], crop))
        save_json(self.path / f"roi_{suffix}.json", {"bounds": bounds, "afterHostMonotonic": after,
                                                     "samples": [r for r, _ in results]})
        return results


def shape_variants(samples):
    """Count distinct neutral foreground silhouettes, ignoring black/gray selection.

    Both #000 and #808080 fall under 190. A gray-to-black color jump alone
    cannot yield three silhouette variants. Pixel thresholds and raw crops persist.
    """
    masks = []
    differences = []
    for _, image in samples:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mask = gray < 190
        threshold = max(16, int(mask.size * .003))
        dist = [int(np.count_nonzero(mask != prev)) for prev in masks]
        differences.append(dist)
        if not masks or all(d > threshold for d in dist):
            masks.append(mask)
    return len(masks), differences


def still_metrics(samples):
    if len(samples) < 3:
        raise AssertionError("Need at least three genuine timed image samples to prove stillness")
    first = samples[0][1].astype(np.int16)
    values = []
    for _, image in samples[1:]:
        diff = np.max(np.abs(image.astype(np.int16) - first), axis=2)
        values.append({"meanDelta": float(diff.mean()), "changedFractionOver5": float((diff > 5).mean())})
    return values
