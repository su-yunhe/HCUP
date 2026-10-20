import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--run", required=True)
parser.add_argument("--previous")
args = parser.parse_args()
versions = Path(__file__).resolve().parent / "script-versions"
target = versions / args.run
target.mkdir(parents=True, exist_ok=False)
hashes = {}
for name in ("test_main_tabs.py", "evidence.py"):
    source = ROOT / "hypium_tests" / name
    data = source.read_bytes()
    (target / name).write_bytes(data)
    hashes[name] = hashlib.sha256(data).hexdigest()
    if args.previous:
        previous = versions / args.previous / name
        diff = ''.join(difflib.unified_diff(previous.read_text().splitlines(True), data.decode().splitlines(True),
            fromfile=f"{args.previous}/{name}", tofile=f"{args.run}/{name}"))
        (versions / f"{args.previous}-to-{args.run}-{name}.diff").write_text(diff, encoding="utf-8")
(target / "sha256.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
print(json.dumps(hashes))
