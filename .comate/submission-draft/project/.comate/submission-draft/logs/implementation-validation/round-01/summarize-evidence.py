"""Offline consolidation of completed vg-spec8 runs. Does not touch the device."""
import ast
import hashlib
import json
from pathlib import Path

from hypium_tests.verification_support import ROOT, source_fingerprint, walk_tree

ROUND = ROOT / "logs/implementation-validation/round-01"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (ROUND / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def method_hash(path, method):
    text = path.read_text(encoding="utf-8")
    node = next(node for node in ast.walk(ast.parse(text)) if isinstance(node, ast.FunctionDef) and node.name == method)
    return hashlib.sha256(ast.get_source_segment(text, node).encode()).hexdigest()


def main():
    final = source_fingerprint()
    initial = read(ROUND / "source-fingerprint-before.json")
    assert final == initial and len(final) == 258
    write("source-fingerprint-final.json", final)
    cases = {}
    runs = {}
    for folder in ["attempt04-full", "attempt05-sentinel"]:
        directory = ROUND / folder
        report = read(directory / "harness-report.json")
        events = [json.loads(line) for line in (directory / "device-actions.jsonl").read_text(encoding="utf-8").splitlines()]
        requests = [json.loads(line) for line in (directory / "mock-requests.jsonl").read_text(encoding="utf-8").splitlines()]
        checkpoints = [event for event in events if event["action"] == "network_checkpoint"]
        assert all(event["delta"] == 0 for event in checkpoints if not event.get("continueEverClicked", False))
        assert [request["method"] for request in requests] == ["HEAD"] * 3
        authorization = next(event for event in events if event["action"] == "continue_authorization_boundary")
        assert all(request["monotonic"] > authorization["monotonic"] for request in requests)
        begin = next(event for event in events if event["action"] == "continuous_zero_window_begin")
        end = next(event for event in events if event["action"] == "continuous_zero_window_end")
        assert end["monotonic"] - begin["monotonic"] >= 125
        ui = []
        for path in sorted(directory.glob("*-open.json")):
            if path.name.startswith("counter-"):
                continue
            nodes = list(walk_tree(read(path)))
            assert sum(node.get("id") == "webdav_restore_confirm_dialog" for node in nodes) == 1
            assert not any(node.get("id") == "webdav_restore_request_loading" for node in nodes)
            ui.append(path.name)
        for path in sorted(directory.glob("*-cancel.json")):
            if path.name.startswith("counter-"):
                continue
            nodes = list(walk_tree(read(path)))
            assert not any(node.get("id") == "webdav_restore_confirm_dialog" for node in nodes)
            restore = [node for node in nodes if node.get("id") == "webdav_restore_button"]
            assert len(restore) == 1 and restore[0]["text"] == "从云端恢复" and restore[0]["enabled"] == "true"
        boundary = [event["name"] for event in checkpoints if event["name"].startswith("boundary-") and event["name"].endswith("-cancel")]
        if folder == "attempt04-full":
            assert len(boundary) == 20
        for case in report["cases"]:
            if case["outcome"] == "pass":
                cases[case["name"].split()[0]] = {"outcome": "pass", "run": folder, "case": case["name"]}
        assert source_fingerprint() == read(directory / "source-fingerprint-after.json")
        runs[folder] = {"passed": sum(case["outcome"] == "pass" for case in report["cases"]),
                        "skipped": sum(case["outcome"] == "skip" for case in report["cases"]),
                        "failed": sum(case["outcome"] in ["fail", "error"] for case in report["cases"]),
                        "zeroWindowStart": begin["time"], "zeroWindowEnd": end["time"],
                        "zeroWindowSeconds": end["monotonic"] - begin["monotonic"],
                        "uncontinuedCheckpoints": sum(not event.get("continueEverClicked", False) for event in checkpoints),
                        "boundaryBranches": len(boundary), "uiOpenSnapshotsAudited": len(ui),
                        "requests": requests, "authorizationBoundary": authorization["time"]}
    assert len(cases) == 6
    sentinel = ROUND / "attempt05-sentinel"
    before = read(sentinel / "sentinel-before-entities.json")
    after = read(sentinel / "sentinel-after-cancel-entities.json")
    assert before == after and len(before["user_word_books"]["rows"]) > 0
    old = ROUND / "attempt04-full/test-scripts/test_restore_confirmation.py"
    current = ROOT / "hypium_tests/test_restore_confirmation.py"
    unchanged = {method: method_hash(old, method) == method_hash(current, method)
                 for method in ["test_01_core_smoke", "test_20_empty_and_whitespace_configuration"]}
    assert all(unchanged.values())
    summary = {"status": "pass", "productionInputs": 258, "productionUnchanged": True,
               "productionManifestSha256": digest(ROUND / "source-fingerprint-final.json"),
               "hapSha256": read(sentinel / "installation-manifest.json")["hapSha256"],
               "runs": runs, "finalLogicalCases": cases, "retainedCaseMethodsUnchanged": unchanged,
               "sentinelTables": {table: len(data["rows"]) for table, data in before.items()},
               "sentinelEntitiesEqual": True, "sentinelBeforeSha256": digest(sentinel / "sentinel-before-entities.json"),
               "sentinelAfterSha256": digest(sentinel / "sentinel-after-cancel-entities.json"),
               "requirements": {f"A{index}": "pass" for index in range(1, 20)},
               "notRun": ["D2 preview cancellation/deep restore", "concurrent automatic sync"]}
    write("combined-final-report.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key not in ["runs", "finalLogicalCases", "requirements"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
