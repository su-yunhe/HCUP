"""Create auditable metrics from completed local runner/HTTP/UI records."""
import collections
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
base = root / "traces/implementation-validation"
runs = sys.argv[1:]
summary = {"runs": [], "outcomes": {}, "official_result": "not_available"}
fingerprints = []
for name in runs:
    folder = base / name
    report = json.loads((folder / "selftest.json").read_text(encoding="utf-8"))
    network = [json.loads(line) for line in (folder / "webdav-requests.jsonl").read_text(encoding="utf-8").splitlines()]
    ui = [json.loads(line) for line in (folder / "ui-events.jsonl").read_text(encoding="utf-8").splitlines()]
    requests = {row["request_id"]: row for row in network if row["event"] == "request"}
    responses = {row["request_id"]: row for row in network if row["event"] == "response"}
    overlaps = []
    for row in ui:
        if row["event"] != "ui_loading_sample":
            continue
        matching = [request_id for request_id in row["active_request_ids"]
                    if requests[request_id]["epoch"] <= row["epoch"] <= responses[request_id]["epoch"]
                    and requests[request_id]["auth_matches_fixture"]
                    and requests[request_id]["root"] == row["root"]]
        assert matching, f"Non-overlapping loading sample in {name}: {row}"
        overlaps.append({"test": row["test"], "epoch": row["epoch"], "root": row["root"],
                         "request_ids": matching})
    durations = {request_id: responses[request_id]["epoch"] - request["epoch"]
                 for request_id, request in requests.items() if request_id in responses}
    terminals = [row for row in ui if row["event"] == "sync_terminal"]
    counts = collections.Counter(case["outcome"] for case in report["cases"])
    for case in report["cases"]:
        summary["outcomes"][case["name"]] = case["outcome"]
    for path in sorted(folder.glob("source-fingerprint-*.json")):
        content = json.loads(path.read_text(encoding="utf-8"))
        fingerprints.append(content)
    summary["runs"].append({"run": name, "report": str(folder.relative_to(root) / "selftest.json"),
                            "runner_exit": int((folder / "selftest-exit.txt").read_text().strip()),
                            "counts": dict(counts), "environment_warnings": report["env_warnings"],
                            "requests": len(requests), "responses": len(responses),
                            "methods": dict(collections.Counter(row["method"] for row in requests.values())),
                            "max_request_seconds": max(durations.values(), default=0),
                            "loading_network_overlaps": overlaps, "terminals": terminals,
                            "long_chains": [row for row in ui if row["event"] == "long_chain_complete"]})
assert fingerprints and all(item == fingerprints[0] for item in fingerprints), "Frozen production fingerprints differ"
summary["source_integrity"] = {"all_fingerprints_equal": True, "files": len(fingerprints[0]),
                               "manifest_sha256": hashlib.sha256(json.dumps(fingerprints[0], sort_keys=True).encode()).hexdigest()}
(base / "round02-validation-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"runs": [{key: row[key] for key in ("run", "counts", "requests", "responses", "max_request_seconds")}
                            for row in summary["runs"]], "source_integrity": summary["source_integrity"]}, indent=2))
