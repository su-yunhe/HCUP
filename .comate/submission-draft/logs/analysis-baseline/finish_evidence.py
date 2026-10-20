import hashlib
import json
import pathlib
from datetime import datetime, timezone

root = pathlib.Path(__file__).resolve().parents[2]
out = root / "logs/analysis-baseline"
build_dirs = [root / ".hvigor", root / "entry/build"]
for kind in ("core", "feature"):
    build_dirs.extend(p / "build" for p in (root / kind).iterdir() if p.is_dir() and (p / "build").exists())
generated = []
for directory in build_dirs:
    files = [p for p in directory.rglob("*") if p.is_file()]
    generated.append({"directory": directory.relative_to(root).as_posix(), "count": len(files), "bytes": sum(p.stat().st_size for p in files), "files": [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()} for p in files]})
(out / "build-generated-manifest.json").write_text(json.dumps(generated, ensure_ascii=False, indent=2), encoding="utf-8")
commands = []
for p in sorted(out.glob("*.command.json")):
    commands.append({"record": p.name, "data": json.loads(p.read_text(encoding="utf-8-sig"))})
(out / "command-index.json").write_text(json.dumps(commands, ensure_ascii=False, indent=2), encoding="utf-8")
important = ["build-full.log", "build-result.json", "warning-inventory.csv", "warning-summary.json", "baseline-pristine-unsigned.hap", "25-install-repro.stdout.log", "17-device-abi.stdout.log", "15-screen-installed.png", "13-layout-installed.json", "environment-check.log"]
manifest = {n: {"sha256": hashlib.sha256((out / n).read_bytes()).hexdigest(), "bytes": (out / n).stat().st_size} for n in important}
(out / "evidence-sha256.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"generated_directories": len(generated), "generated_files": sum(g["count"] for g in generated), "captured_commands": len(commands), "important_evidence": manifest}, indent=2))
