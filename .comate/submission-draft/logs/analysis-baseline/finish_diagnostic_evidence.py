import hashlib
import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
log = root / "logs/analysis-baseline"
names = [
    "abi-diagnostic-build-full.log", "abi-diagnostic-build-result.json",
    "abi-diagnostic-v2-build-full.log", "abi-diagnostic-v2-build-result.json", "abi-diagnostic-v2-integrity.json",
    "abi-diagnostic-v3-build-full.log", "abi-diagnostic-v3-build-result.json", "abi-diagnostic-v3-integrity.json",
    "abi-diagnostic-v3-config.diff", "abi-filter-sdk-schema-excerpt.json",
    "d30-install-v3.stdout.log", "d31-start-v3.stdout.log", "d33-app-ready.png", "d33-app-ready.json",
    "d36-after-home-phone.png", "d36-after-home-phone.json", "d39-category-tab.png", "d39-category-tab.json",
    "d41-after-category-leaf.png", "d41-after-category-leaf.json", "d56-search-entered.png", "d56-search-entered.json",
    "d57-search-submit.command.json", "d58-goods-category.png", "d58-goods-category.json",
    "d59-goods-category-settled.png", "d59-goods-category-settled.json", "d47-app-log-all.stdout.log",
    "fingerprint-after-diagnostic-ui.json", "dependencies-before-diagnostic.json", "dependencies-after-diagnostic-v3.json",
    "emulator-stop.command.json", "emulator-stop.log", "targets-after-stop-settled.log", "command-index.json",
    "abi-diagnostic-v3/entry/build/default/outputs/default/entry-default-unsigned.hap"
]
manifest = {n: {"sha256": hashlib.sha256((log / n).read_bytes()).hexdigest(), "bytes": (log / n).stat().st_size} for n in names}
(log / "diagnostic-evidence-sha256.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
def walk(node):
    yield node.get("attributes", {})
    for child in node.get("children", []):
        yield from walk(child)
attrs = list(walk(json.loads((log / "d59-goods-category-settled.json").read_text(encoding="utf-8"))))
result = {
    "scope": "ABI adapted diagnostic v3 only; pristine installation remains blocked",
    "hap_sha256": manifest["abi-diagnostic-v3/entry/build/default/outputs/default/entry-default-unsigned.hap"]["sha256"],
    "final_target_snapshot": "d59-goods-category-settled.json",
    "text_input_count": sum(a.get("type") in ("TextInput", "Search") for a in attrs),
    "grid_count": sum(a.get("type") == "Grid" for a in attrs),
    "list_count": sum(a.get("type") == "List" for a in attrs),
    "filter_text_count": sum(a.get("text") == "筛选" for a in attrs),
    "sort_text_count": sum(a.get("text") == "排序" for a in attrs),
    "placeholder_count": sum(a.get("text") == "商品分类页面内容视图" for a in attrs),
    "category_before_after_png_identical": manifest["d39-category-tab.png"]["sha256"] == manifest["d41-after-category-leaf.png"]["sha256"],
}
original_before = json.loads((log / "dependencies-before-diagnostic.json").read_text())
original_after = json.loads((log / "dependencies-after-diagnostic-v3.json").read_text())
result["original_dependency_changes"] = [n for n in original_before.keys() | original_after.keys() if original_before.get(n) != original_after.get(n)]
(log / "diagnostic-ui-observations.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
generated = []
for version in ("abi-diagnostic", "abi-diagnostic-v2", "abi-diagnostic-v3"):
    diag = log / version
    dirs = [diag / ".hvigor", diag / "entry/build"]
    for kind in ("core", "feature"):
        dirs.extend(p / "build" for p in (diag / kind).iterdir() if p.is_dir() and (p / "build").is_dir())
    for d in dirs:
        if d.exists():
            files = [p for p in d.rglob("*") if p.is_file()]
            generated.append({"directory": d.relative_to(root).as_posix(), "files": len(files), "bytes": sum(p.stat().st_size for p in files)})
(log / "diagnostic-generated-manifest.json").write_text(json.dumps(generated, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
print("Diagnostic generated directories:", len(generated))
