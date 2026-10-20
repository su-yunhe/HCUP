"""Create a task-local source clone with one explicitly authorized packaging difference."""
import difflib
import hashlib
import json
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parents[2]
log = root / "logs/analysis-baseline"
prefix = sys.argv[1] if len(sys.argv) > 1 else "abi-diagnostic"
copy_dependencies = len(sys.argv) > 2 and sys.argv[2] == "copy-dependencies"
exclude_arm64 = "exclude-arm64" in sys.argv[2:]
diag = log / prefix
approved = json.loads((root / "workflow/analysis-start-code-fingerprint.json").read_text(encoding="utf-8-sig"))
if diag.exists():
    raise RuntimeError("Diagnostic destination already exists; refusing to overwrite")
for name, digest in approved["tracked_files_sha256"].items():
    source = root / name
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != digest:
        raise RuntimeError("Baseline source changed: " + name)
    dest = diag / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
config = diag / "entry/build-profile.json5"
original = config.read_bytes()
newline = b"\r\n" if b"\r\n" in original else b"\n"
needle = b'  "buildOption": {'
insertion = newline.join([needle, b'    "externalNativeOptions": {', b'      "abiFilters": ["x86_64"]', b'    },'])
if exclude_arm64:
    insertion += newline + newline.join([b'    "nativeLib": {', b'      "filter": {', b'        "excludes": ["**/arm64-v8a/**"]', b'      }', b'    },'])
assert original.count(needle) == 1
adapted = original.replace(needle, insertion, 1)
config.write_bytes(adapted)
(log / (prefix + "-config.diff")).write_text("".join(difflib.unified_diff(original.decode().splitlines(True), adapted.decode().splitlines(True), fromfile="baseline/entry/build-profile.json5", tofile=prefix + "/entry/build-profile.json5")), encoding="utf-8")
links = []
module_roots = [pathlib.PurePosixPath(n).parent for n in approved["tracked_files_sha256"] if n.endswith("oh-package.json5")]
def mirror_deps(source, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = item.resolve()
        output = dest / item.name
        is_link = item.is_symlink() or item.is_junction()
        if is_link or (item.name == ".ohpm" and not copy_dependencies):
            try:
                rel = target.relative_to(root)
            except ValueError:
                raise RuntimeError("Unexpected dependency target outside this task: " + str(target))
            # Local project module aliases must resolve into this diagnostic copy.
            rebased = diag / rel if copy_dependencies or rel.parts[0] in ("core", "feature") else target
            links.append({"link": str(output), "target": str(rebased), "scope": "diagnostic-local-module" if rebased != target else "read-only-original-third-party"})
        elif item.is_dir():
            mirror_deps(item, output)
        elif item.is_file():
            shutil.copyfile(item, output)
for module in module_roots:
    source = root / module / "oh_modules"
    if source.is_dir():
        mirror_deps(source, diag / module / "oh_modules")
(log / (prefix + "-dependency-links.json")).write_text(json.dumps(links, indent=2), encoding="utf-8")
manifest = {"root": str(diag), "copied_tracked_count": len(approved["tracked_files_sha256"]), "head_source": approved["head"], "only_authorized_difference": "entry/build-profile.json5 buildOption.externalNativeOptions.abiFilters=[x86_64]", "baseline_config_sha256": hashlib.sha256(original).hexdigest(), "diagnostic_config_sha256": hashlib.sha256(adapted).hexdigest(), "dependency_install_run": False, "manual_hap_repack": False, "dependency_links": len(links)}
manifest["dependencies_physically_copied_unchanged"] = copy_dependencies
if exclude_arm64:
    manifest["only_authorized_difference"] += "; nativeLib.filter.excludes=[**/arm64-v8a/**]"
(log / (prefix + "-preparation.json")).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
