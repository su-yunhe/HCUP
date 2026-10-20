import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path('D:/HCUP/vg-spec8')
DRAFT = ROOT / '.comate/submission-draft'
OUT = DRAFT / 'validation/independent-rebuild'
ROUND = sys.argv[1] if len(sys.argv) > 1 else 'round03'
CLONE = OUT / ROUND / 'baseline'
BASE = '9cbcf7292c8cc46955dc3b522ddbda41c66a61d9'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while chunk := f.read(1024*1024): h.update(chunk)
    return h.hexdigest()

env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
result = {'started_at': datetime.now(timezone.utc).isoformat(), 'environment': {
    'entry': 'D:/hongmengcup/Enter-HarmonyEnv.ps1', 'python': sys.version,
    'python_executable': sys.executable, 'platform': platform.platform()}}
snapshots = json.loads((DRAFT / 'traces/code-changes/index.json').read_text(encoding='utf-8'))
failures = []
commands = []
for row in snapshots['files']:
    name = row['path']
    final = DRAFT / 'traces/code-changes/final' / name
    if not (sha(final) == row['final_sha256'] == sha(DRAFT / 'project' / name) == sha(ROOT / name)):
        failures.append(name + ':final')
    args = ['git', 'show', BASE + ':' + name]
    p = subprocess.run(args, cwd=CLONE, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    index = len(commands)+1
    (OUT / f'supplement-{index:02d}-stderr.log').write_bytes(p.stderr)
    commands.append({'command':args, 'cwd':str(CLONE), 'exit_code':p.returncode,
                     'stdout_bytes':len(p.stdout), 'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
                     'stderr':f'supplement-{index:02d}-stderr.log', 'expected_absent':not row['base_present']})
    if row['base_present']:
        base = DRAFT / 'traces/code-changes/base' / name
        if p.returncode or not (sha(base) == row['base_blob_sha256'] == hashlib.sha256(p.stdout).hexdigest()):
            failures.append(name + ':base')
    elif p.returncode == 0 or (DRAFT / 'traces/code-changes/base' / name).exists():
        failures.append(name + ':unexpected-base')
templates = json.loads((DRAFT / 'provenance/template-hashes.json').read_text(encoding='utf-8'))
template_failures = []
for row in templates:
    if not (sha(Path('D:/SWE-OpenHarmony/templates') / row['path']) == row['sha256'] ==
            sha(DRAFT / 'provenance/templates' / row['path'])):
        template_failures.append(row['path'])
result.update({'code_snapshots':{'status':'pass' if not failures else 'fail','files':len(snapshots['files']),
                               'failures':failures,'commands':commands},
               'official_template_copies':{'status':'pass' if not template_failures else 'fail',
                                         'files':len(templates),'failures':template_failures}})
result['passed'] = not failures and not template_failures
result['ended_at'] = datetime.now(timezone.utc).isoformat()
(OUT / 'supplement-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
sys.exit(0 if result['passed'] else 1)
