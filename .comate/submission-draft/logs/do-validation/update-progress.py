import json
import re
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[2]
record_path = root / "workflow/verification/do-progress-v1.json"
record = json.loads(record_path.read_text(encoding="utf-8"))
completed = []
for run in (7, 8, 9, 10, 11):
    if not (root / f"logs/do-validation/runner-v{run}.log").exists():
        continue
    log = (root / f"logs/do-validation/runner-v{run}.log").read_text(encoding="utf-8-sig")
    for name in re.findall(r"^(test_\w+) \(.*?\.\.\. ok$", log, re.M):
        if run == 7 and not name.startswith(("test_01_", "test_02_", "test_03_")):
            continue
        if run == 8 and not name.startswith(("test_04_", "test_05_", "test_06_", "test_07_", "test_08_")):
            continue
        completed.append({"test": name, "status": "pass", "batch": run,
                          "log": f"logs/do-validation/runner-v{run}.log"})
record["utc"] = datetime.now(timezone.utc).isoformat()
record["completed_unique_methods"] = completed
record["active_batch"] = max(run for run in range(7, 12) if (root / f"logs/do-validation/runner-v{run}.log").exists())
record["remaining"] = [index for index in range(1, 12)
                       if not any(case["test"].startswith(f"test_{index:02}_") for case in completed)]
record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"completed": len(completed), "remaining": record["remaining"]}))
