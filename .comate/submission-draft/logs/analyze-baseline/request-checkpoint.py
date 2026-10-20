import json
from pathlib import Path
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
events = [json.loads(line) for line in (root / "server-requests.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
row = {"time": datetime.now(timezone.utc).isoformat(), "label": sys.argv[1],
       "server_events": len(events),
       "request_begin_count": sum(item["kind"] == "request_begin" for item in events),
       "response_count": sum(item["kind"] == "response" for item in events),
       "state": json.loads((root / "server-state.json").read_text(encoding="utf-8-sig"))}
with (root / "request-checkpoints.jsonl").open("a", encoding="utf-8") as output:
    output.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps(row, ensure_ascii=False))
