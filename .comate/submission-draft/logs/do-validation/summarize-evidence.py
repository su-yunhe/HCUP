"""Build an auditable operation timeline from raw local UI/server observations."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
run = int(sys.argv[1]) if len(sys.argv) > 1 else 7
folder = root / f"logs/do-validation/device-run-v{run}"
ui = [json.loads(line) for line in (folder / "ui-events.jsonl").read_text(encoding="utf-8").splitlines()]
server = [json.loads(line) for line in (folder / "server.jsonl").read_text(encoding="utf-8").splitlines()]
clicks = [record for record in ui if record["event"] == "manual_click"]
operations = []
for index, click in enumerate(clicks):
    next_click = clicks[index + 1]["monotonic_ns"] if index + 1 < len(clicks) else 10**30
    idle = next((r for r in ui if r["event"] == "idle_observed" and
                 click["monotonic_ns"] < r["monotonic_ns"] < next_click), None)
    end = idle["monotonic_ns"] if idle else next_click
    requests = [r for r in server if r["event"] == "request" and
                click["monotonic_ns"] <= r["monotonic_ns"] < end]
    ids = {r["id"] for r in requests}
    replies = [r for r in server if r.get("id") in ids and r["event"] != "request"]
    captures = [r for r in ui if r["event"] == "capture_end" and
                click["monotonic_ns"] < r["monotonic_ns"] < end and
                (r.get("loading") or {}).get("type") == "LoadingProgress" and
                (r.get("loading") or {}).get("visible") == "true"]
    order = [{"capture": c["file"], "ui_observation_upper_ns": c["monotonic_ns"],
              "later_request_id": r["id"], "request_received_ns": r["monotonic_ns"]}
             for c in captures for r in requests if c["monotonic_ns"] <= r["monotonic_ns"]]
    raw_samples = [r for r in ui if r["event"] == "fast_raw_sample" and r.get("loading") and
                   click["monotonic_ns"] <= r["snapshot_start_ns"] < end]
    raw_order = [{"capture": c["file"], "ui_observation_upper_ns": c["snapshot_end_ns"],
                  "later_request_id": r["id"], "request_received_ns": r["monotonic_ns"]}
                 for c in raw_samples for r in requests if c["snapshot_end_ns"] <= r["monotonic_ns"]]
    operations.append({"test": click["test"], "label": click.get("label"), "attempt": click.get("attempt"),
                       "click": click, "idle": idle, "requests": requests, "responses_or_disconnects": replies,
                       "visible_loading_captures": [c["file"] for c in captures],
                       "completed_ui_before_later_real_request": order + raw_order})
result = {"run": run, "operations": operations,
          "limitation": "Finite observed UI samples; no claim to inspect every rendered frame or hidden tests.",
          "request_count": sum(r["event"] == "request" for r in server),
          "fast_order_results": [r for r in ui if r["event"] == "fast_order_result"],
          "timeout_evidence": [r for r in ui if r["event"] == "real_timeout_evidence"],
          "reentry_ages": [r for r in ui if r["event"] in ("reentry_request_age", "foreground_request_age")]}
(folder / "operation-timelines.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"run": run, "operations": len(operations), "requests": result["request_count"],
                  "operations_with_loading_then_later_request": sum(bool(o["completed_ui_before_later_real_request"]) for o in operations),
                  "fast": result["fast_order_results"], "timeout": result["timeout_evidence"]}))
