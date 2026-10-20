"""Check the analysis artifacts against this task's immutable inputs and sources."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
acceptance = (ROOT / 'spec/acceptance.md').read_text('utf-8')
notes = (ROOT / 'spec/baseline-notes.md').read_text('utf-8')
spec = (ROOT / 'spec/requirement.md').read_text('utf-8')
metadata = json.loads((ROOT / 'spec/metadata.json').read_text('utf-8'))
checks = []

def check(name: str, passed: bool, detail: object = None) -> None:
    checks.append({'name': name, 'pass': passed, 'detail': detail})

rows = []
for line in acceptance.splitlines():
    match = re.match(r'^\| A(\d+) \|', line)
    if match:
        rows.append((int(match[1]), [cell.strip() for cell in line.strip('|').split('|')]))
counts = Counter(number for number, _ in rows)
check('A1-A44 each have one atomic/assumption row and one dimensions row',
      counts == Counter({number: 2 for number in range(1, 45)}), dict(sorted(counts.items())))
dimensions = [(number, cells) for number, cells in rows if len(cells) == 9]
check('44 complete eight-dimension rows', len(dimensions) == 44 and
      {n for n, _ in dimensions} == set(range(1, 45)) and all(all(c) for _, c in dimensions))
atomic = [(number, cells) for number, cells in rows if len(cells) != 9]
check('44 atomic/assumption rows with selectors', len(atomic) == 44 and
      all(len(c) == (6 if n < 40 else 7) and all(c) for n, c in atomic))
explicit = sum('SPEC_EXPLICIT' in cells for _, cells in atomic)
derived = sum('REASONABLE_DERIVATION' in cells for _, cells in atomic)
check('28 explicit, 11 derived, five separately marked assumptions', explicit == 28 and
      derived == 11 and sum('UNCONFIRMED_ASSUMPTION' in c for _, c in atomic) == 5 and
      {n for n, _ in atomic if n >= 40} == set(range(40, 45)))
steps = re.findall(r'^\d+\. .+$', spec, re.MULTILINE)
missing_steps = [step for step in steps if step not in acceptance]
check('all 17 numbered Spec steps quoted exactly', len(steps) == 17 and not missing_steps, missing_steps)
overviews = [line for line in spec.splitlines() if line.startswith('用户')]
check('all four scenario overviews quoted exactly', len(overviews) == 4 and all(line in acceptance for line in overviews))
boundaries = ['空输入', '纯空格', '取消', '关闭', '重复点击', '快速连点', '无数据',
              '最后一页', '部分操作', '请求失败', '返回后重进', '重启应用后重进']
check('all requested boundary classes present', all('| ' + b + ' |' in acceptance for b in boundaries))
check('prospective selectors and network applicability documented', '需在实现时补 `.id()`' in acceptance
      and 'stateDiagram-v2' in acceptance and '没有本题强制网络类需求' in acceptance)
check('both final artifact files exist and have substantial content', len(acceptance) > 1000 and len(notes) > 1000)
runtime_files = ['workflow/verification/baseline-r3.md',
                 'traces/baseline-analysis/r3/command-index.csv',
                 'traces/baseline-analysis/r3/artifact-manifest.json']
check('frozen independent runtime report and evidence indexes exist', all((ROOT / name).is_file() for name in runtime_files))
installed = json.loads((ROOT / 'logs/analysis-baseline-r3-install-unsigned.json').read_text('utf-8-sig'))
launched = json.loads((ROOT / 'logs/analysis-baseline-r3-launch-first.json').read_text('utf-8-sig'))
check('runtime installation and launch have successful raw outputs', installed['exit_code'] == 0 and
      'install bundle successfully' in str(installed['output']) and launched['exit_code'] == 0 and
      'start ability successfully' in str(launched['output']))
captures = ['existing-app-window', 'content-left', 'content-up', 'restarted-app-window']
capture_checks = []
for label in captures:
    path = ROOT / 'traces/baseline-analysis/r3' / (label + '-after.png')
    raw = path.read_bytes()
    capture_checks.append(raw[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', raw[16:24]) == (1308, 2880)
                          and (path.parent / (label + '.json')).is_file())
check('all four stable observations have original size screenshots and UI dumps', all(capture_checks))
fingerprint = json.loads((ROOT / 'workflow/analysis-code-fingerprint.json').read_text('utf-8'))
tracked_changes = [name for name, digest in fingerprint['tracked_files_sha256'].items()
                   if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
diff = subprocess.check_output(['git', 'diff', '--numstat'], cwd=ROOT, text=True)
staged = subprocess.check_output(['git', 'diff', '--cached', '--numstat'], cwd=ROOT, text=True)
check('approved HEAD and all 677 tracked files unchanged', head == metadata['base_commit'] and
      len(fingerprint['tracked_files_sha256']) == 677 and not tracked_changes and not diff and not staged,
      {'head': head, 'changed': tracked_changes})
for filename, expected in [('spec/requirement.md', fingerprint['spec_sha256']),
                           ('spec/metadata.json', fingerprint['metadata_sha256'])]:
    check(filename + ' hash unchanged', hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected)

result = {'created_at': datetime.now(timezone.utc).isoformat(), 'scope': 'analysis documents and tracked baseline integrity only',
          'not_a_functional_test': True, 'checks': checks, 'pass': all(c['pass'] for c in checks),
          'artifact_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                              for name in ['spec/acceptance.md', 'spec/baseline-notes.md']}}
(ROOT / 'workflow/analysis-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'pass': result['pass'], 'check_count': len(checks),
                  'failed': [c for c in checks if not c['pass']],
                  'record': 'workflow/analysis-validation.json'}, ensure_ascii=False))
raise SystemExit(0 if result['pass'] else 1)
