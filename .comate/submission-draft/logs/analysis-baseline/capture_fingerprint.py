"""Read-only comparison against the approved analysis-start tracked-file hashes."""
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

root = pathlib.Path(__file__).resolve().parents[2]
approved = json.loads((root / "workflow/analysis-start-code-fingerprint.json").read_text(encoding="utf-8-sig"))
current = {}
missing = []
for name in approved["tracked_files_sha256"]:
    p = root / name
    if p.is_file():
        current[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    else:
        missing.append(name)
changed = [n for n, digest in current.items() if digest.lower() != approved["tracked_files_sha256"][n].lower()]
result = {
    "utc": datetime.now(timezone.utc).isoformat(),
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "approved_head": approved["head"],
    "tracked_count": len(approved["tracked_files_sha256"]),
    "missing": missing,
    "changed": changed,
    "tracked_files_sha256": current,
    "git_status": subprocess.check_output(["git", "status", "--short"], cwd=root, text=True),
    "spec_requirement_sha256": hashlib.sha256((root / "spec/requirement.md").read_bytes()).hexdigest(),
}
dest = root / "logs/analysis-baseline" / (sys.argv[1] + ".json")
dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "tracked_files_sha256"}, ensure_ascii=False, indent=2))
sys.exit(0 if not changed and not missing and result["head"] == approved["head"] else 1)
