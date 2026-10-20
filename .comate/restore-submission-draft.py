"""Check frozen draft hashes; --restore restores the published draft bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

project = Path(__file__).resolve().parent.parent
manifest = json.loads((project / '.comate/submission-draft-publication.json').read_text(encoding='utf-8'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--restore', action='store_true', help='Overwrite tracked draft files with HEAD, keeping their original bytes; download Git LFS objects as needed.')
args = parser.parse_args()
if args.restore:
    raw = subprocess.check_output(['git', '-C', str(project), 'rev-parse', '--git-path', 'info/attributes'], text=True).strip()
    attrs = Path(raw)
    if not attrs.is_absolute():
        attrs = project / attrs
    attrs.parent.mkdir(parents=True, exist_ok=True)
    data = attrs.read_bytes() if attrs.exists() else b''
    rule = b'/.comate/submission-draft/** -text'
    if rule not in data.splitlines():
        attrs.write_bytes(data + (b'\n' if data and not data.endswith(b'\n') else b'') + rule + b'\n')
    subprocess.run(['git', '-C', str(project), 'restore', '--source=HEAD', '--worktree', '--', '.comate/submission-draft'], check=True)
    subprocess.run(['git', '-C', str(project), 'lfs', 'pull'], check=True)
errors = []
for entry in manifest['published_files']:
    path = project / entry['path']
    if not path.is_file():
        errors.append({'path': entry['path'], 'error': 'missing'})
        continue
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            digest.update(block)
    if path.stat().st_size != entry['bytes'] or digest.hexdigest() != entry['sha256']:
        errors.append({'path': entry['path'], 'error': 'size or SHA-256 mismatch'})
print(json.dumps({'checked': len(manifest['published_files']), 'errors': errors}, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
