import hashlib
import json
import pathlib
import sys
import zipfile

root = pathlib.Path(__file__).resolve().parents[2]
log = root / "logs/analysis-baseline"
version = sys.argv[1]
diag = log / version
approved = json.loads((root / "workflow/analysis-start-code-fingerprint.json").read_text(encoding="utf-8-sig"))
differences = [name for name, digest in approved["tracked_files_sha256"].items() if hashlib.sha256((diag / name).read_bytes()).hexdigest() != digest]
before = json.loads((log / "dependencies-before-diagnostic.json").read_text())
dep_diff = [name for name, digest in before.items() if not (diag / name).is_file() or hashlib.sha256((diag / name).read_bytes()).hexdigest() != digest]
hap = diag / "entry/build/default/outputs/default/entry-default-unsigned.hap"
libs = []
if hap.is_file():
    with zipfile.ZipFile(hap) as z:
        libs = [{"name": info.filename, "bytes": info.file_size} for info in z.infolist() if info.filename.endswith(".so")]
result = {"diagnostic": version, "tracked_count": len(approved["tracked_files_sha256"]), "tracked_differences_from_pristine": differences, "copied_dependency_file_count": len(before), "copied_dependency_content_differences": dep_diff, "hap_sha256": hashlib.sha256(hap.read_bytes()).hexdigest() if hap.is_file() else None, "hap_native_libs": libs}
(log / (version + "-integrity.json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
schema = pathlib.Path("D:/HarmonyDev/DevEcoStudio-6.1.0/tools/hvigor/hvigor-ohos-plugin/res/schemas/hvigorfile-configuration/module-schema.json")
lines = schema.read_text().splitlines()
start = next(i for i, line in enumerate(lines) if '"nativeLib": {' in line)
(log / "abi-filter-sdk-schema-excerpt.json").write_text(json.dumps({"source": str(schema), "first_line": start+1, "text": "\n".join(lines[start:start+100])}, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if differences != ["entry/build-profile.json5"] or dep_diff:
    sys.exit(1)
