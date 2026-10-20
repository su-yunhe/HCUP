"""Snapshot only registered, dedicated cml-spec7 sessions; exclude setup overview."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4


root = Path(__file__).resolve().parent.parent
state_path = root / "workflow/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
source = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
destination = root / "traces/native" / stamp
destination.mkdir(parents=True)
known = {x["agent_id"] for x in state["sessions"] if x.get("session_id") and not x.get("excluded_from_task_evidence")}
selected = sorted({str(UUID(x["session_id"])) for x in state["sessions"] if x.get("session_id") and not x.get("excluded_from_task_evidence")})
gaps = ["Native UUID unavailable: " + x["agent_id"] for x in state["sessions"] if not x.get("session_id") and x["agent_id"] not in known]
copied = []
for session_id in selected:
    paths = list(source.rglob("*-" + session_id + ".jsonl")) if source.exists() else []
    if not paths:
        gaps.append("Native session file not found: " + session_id)
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
            gaps.append("Skipped unsafe native path for " + session_id)
            continue
        raw = path.read_bytes()
        try:
            header = json.loads(raw.split(b"\n", 1)[0])
            if header.get("type") != "session_meta" or header.get("payload", {}).get("id") != session_id:
                raise ValueError("session metadata mismatch")
        except (ValueError, UnicodeError):
            gaps.append("Unrecognized native session header: " + session_id)
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        copied.append({"session_id": session_id, "source": str(path), "snapshot": target.relative_to(root).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "ends_with_newline": raw.endswith(b"\n")})
result = {"created_at": datetime.now(timezone.utc).isoformat(), "files": copied, "gaps": gaps, "excluded_sessions": [x["session_id"] for x in state["sessions"] if x.get("excluded_from_task_evidence")], "snapshot_only": True, "includes_future_events": False}
(destination / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
previous_native = set(state.get("native_snapshot_gaps", []))
state["record_gaps"] = [gap for gap in state.get("record_gaps", []) if gap not in previous_native] + gaps
state["native_snapshot_gaps"] = gaps
state["last_trace_snapshot"] = (destination / "manifest.json").relative_to(root).as_posix()
state["trace_exclusion_note"] = "Initialization overview deliberately excluded under AGENTS.md; it is not task development evidence. Snapshots include only content written before capture."
state["updated_at"] = result["created_at"]
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"copied": len(copied), "gaps": gaps, "manifest": state["last_trace_snapshot"]}, ensure_ascii=False))
