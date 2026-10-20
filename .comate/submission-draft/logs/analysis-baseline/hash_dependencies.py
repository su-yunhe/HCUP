import hashlib
import json
import pathlib
import sys
root = pathlib.Path(__file__).resolve().parents[2]
files = {}
stack = [root / "oh_modules/.ohpm"]
while stack:
    directory = stack.pop()
    for p in directory.iterdir():
        if p.is_symlink() or p.is_junction():
            continue
        if p.is_dir():
            stack.append(p)
        elif p.is_file():
            files[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
out = root / "logs/analysis-baseline" / (sys.argv[1] + ".json")
out.write_text(json.dumps(files, indent=2), encoding="utf-8")
print("Original physical dependency files hashed:", len(files), "to", out)
