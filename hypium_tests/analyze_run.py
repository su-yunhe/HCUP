"""Recompute authorization-window counts from the original append-only ledger."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
events = [json.loads(line) for line in (args.evidence / "endpoint-events.jsonl").read_text(encoding="utf-8").splitlines()]
open_labels = {"restore_entry_dispatch", "rapid_entry_dispatch"}
continue_labels = {"continue_dispatch", "rapid_continue_dispatch"}
windows = []
for start in events:
    if start.get("label") not in open_labels:
        continue
    later = [item for item in events if item["seq"] > start["seq"]]
    end = next((item for item in later if item.get("label") in open_labels | continue_labels | {"test_end"}), None)
    if end is None:
        windows.append({"start_seq": start["seq"], "status": "incomplete"})
        continue
    observed = [item for item in later if item["seq"] < end["seq"]
                and item["event"] in {"tcp_accept", "http_request"}]
    windows.append({"test": start.get("test"), "round": start.get("round"),
                    "start_seq": start["seq"], "end_seq": end["seq"],
                    "start_utc": start["utc"], "end_utc": end["utc"],
                    "duration_seconds": (end["monotonic_ns"] - start["monotonic_ns"]) / 1e9,
                    "end_reason": end.get("label"),
                    "tcp_connections": sum(item["event"] == "tcp_accept" for item in observed),
                    "all_http_requests": sum(item["event"] == "http_request" for item in observed),
                    "status": "pass" if not observed else "fail", "violations": observed})
authorized = []
for start in events:
    if start.get("label") not in continue_labels:
        continue
    end = next((item for item in events if item["seq"] > start["seq"] and
                item.get("label") in open_labels | {"test_end"}), events[-1])
    requests = [item for item in events if start["seq"] < item["seq"] < end["seq"]
                and item["event"] == "http_request"]
    authorized.append({"test": start.get("test"), "authorization_seq": start["seq"],
                       "authorization_utc": start["utc"], "end_seq": end["seq"], "requests": requests})
result = {"unauthorized_windows": windows, "authorized_flows": authorized,
          "dismiss_capabilities": [item for item in events if item.get("label") == "dismiss_capability"],
          "precontinue_tcp_total": sum(item.get("tcp_connections", 0) for item in windows),
          "precontinue_http_total": sum(item.get("all_http_requests", 0) for item in windows),
          "window_count": len(windows),
          "window_status": "pass" if windows and all(item["status"] == "pass" for item in windows) else "fail"}
(args.evidence / "window-analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({key: result[key] for key in ("window_count", "precontinue_tcp_total", "precontinue_http_total", "window_status")}, ensure_ascii=False))
