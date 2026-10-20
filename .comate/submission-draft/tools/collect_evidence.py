"""Export only task-owned Codex records; derived Markdown never replaces JSONL."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import collections
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
STORE = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
EXCLUDED = {'01a13fc4-2611-7761-a580-1283e0c70541': 'Cross-task initialization overview; not read or exported.'}

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def main():
    stamp = datetime.now(timezone.utc).isoformat()
    state = json.loads((ROOT / 'workflow/state.json').read_text(encoding='utf-8'))
    registered = {x['session_id'] for x in state['sessions'] if x.get('session_id')} - set(EXCLUDED)
    search = {}
    candidates = set()
    for label, query in [('task_id', 'cml-spec17'), ('workspace_windows', str(ROOT)), ('workspace_json_escaped', str(ROOT).replace('\\', '\\\\')), ('workspace_slashes', ROOT.as_posix())]:
        r = subprocess.run(['rg', '-l', '-F', '--glob', '*.jsonl', query, str(STORE / 'sessions')], capture_output=True)
        if r.returncode not in (0, 1):
            raise RuntimeError(r.stderr.decode(errors='replace'))
        hits = [Path(x) for x in r.stdout.decode().splitlines() if x]
        candidates.update(hits)
        search[label] = {'query': query, 'exit_code': r.returncode, 'candidate_files': len(hits)}
    for sid in registered:
        candidates.update((STORE / 'sessions').rglob('*-' + sid + '.jsonl'))
    selected = {}
    excluded = []
    outside_task_hits = 0
    for p in sorted(candidates):
        if any(s in p.name for s in EXCLUDED):
            excluded.append({'session_id': next(s for s in EXCLUDED if s in p.name), 'reason': 'Cross-task overview excluded before reading.'})
            continue
        with p.open(encoding='utf-8') as f:
            first = json.loads(f.readline())
        q = first.get('payload', {})
        sid = q.get('id')
        cwd = q.get('cwd', '').replace('\\', '/').rstrip('/').lower()
        if sid not in registered and cwd != ROOT.as_posix().lower():
            outside_task_hits += 1
            continue
        if first.get('type') != 'session_meta' or not sid:
            raise ValueError('Invalid task native header: ' + str(p))
        selected[sid] = (p, q)
    index = STORE / 'session_index.jsonl'
    index_lines = []
    index_ids = set()
    if index.exists():
        for line in index.read_text(encoding='utf-8').splitlines():
            try: row = json.loads(line)
            except ValueError: continue
            if row.get('id') in selected:
                index_lines.append(line)
                index_ids.add(row['id'])
    dest = OUT / 'traces'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'session-index.filtered.jsonl').write_text('\n'.join(index_lines) + '\n', encoding='utf-8')
    records = []
    gaps = []
    for sid, (src, meta) in sorted(selected.items()):
        source_raw = src.read_bytes()
        raw = source_raw[:source_raw.rfind(b'\n') + 1]
        if not raw:
            raise ValueError('No complete native records: ' + str(src))
        target = dest / 'native' / src.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        contexts = []
        usage = None
        tools = collections.Counter()
        rules = []
        markdown = ['# Codex 原生记录的派生阅读副本', '', f'会话：`{sid}`', '', '此副本按原生行逐项展示；原始 JSONL 为权威记录。保留失败、工具返回及未采用方案。无侧边栏人工 Markdown 导出，不能将本文件称为 IDE 导出。', '']
        failures = []
        for no, line in enumerate(raw.splitlines(), 1):
            try: row = json.loads(line)
            except ValueError:
                gaps.append({'session_id': sid, 'line': no, 'reason': 'Incomplete or unparsable native line retained.'})
                continue
            p = row.get('payload', {})
            if row.get('type') == 'turn_context':
                contexts.append({k: p.get(k) for k in ('model', 'effort', 'reasoning_effort', 'approval_policy', 'cwd') if p.get(k) is not None})
            if row.get('type') == 'event_msg' and p.get('type') == 'token_count':
                usage = p.get('info')
            if row.get('type') == 'response_item' and p.get('type') in ('function_call', 'custom_tool_call'):
                tools[p.get('name', 'unknown')] += 1
            if 'appliedRuleNames' in p:
                rules.append(p['appliedRuleNames'])
            text = json.dumps(p, ensure_ascii=False)
            if any(x in text.lower() for x in ('error', 'failed', 'failure', '失败', '重试')):
                failures.append(no)
            markdown.extend([f'## 原生行 {no} · {row.get("type", "")} · {row.get("timestamp", "")}', '', '````json', json.dumps(row, ensure_ascii=False), '````', ''])
        md = dest / 'markdown' / (sid + '.md')
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text('\n'.join(markdown), encoding='utf-8')
        spawn = meta.get('source', {})
        spawn = spawn.get('subagent', {}).get('thread_spawn', {}) if isinstance(spawn, dict) else {}
        records.append({'session_id': sid, 'native_id': meta.get('id'), 'sidebar_id': sid if sid in index_ids else None,
                        'sidebar_relationship': 'Native session_meta.id equals filtered session_index.id' if sid in index_ids else 'Subagent has native UUID; independent sidebar row not exposed',
                        'agent_path': spawn.get('agent_path'), 'agent_role': meta.get('agent_role'), 'parent_thread_id': spawn.get('parent_thread_id'),
                        'cli_version': meta.get('cli_version'), 'originator': meta.get('originator'), 'source': str(src), 'native': target.relative_to(OUT).as_posix(),
                        'source_bytes_at_read': len(source_raw), 'source_sha256_at_read': hashlib.sha256(source_raw).hexdigest(),
                        'incomplete_tail_bytes_excluded': len(source_raw) - len(raw),
                        'bytes': len(raw), 'sha256': sha(target), 'last_native_timestamp': row.get('timestamp'),
                        'last_native_beijing': datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8))).isoformat() if row.get('timestamp') else None,
                        'ends_with_newline': raw.endswith(b'\n'),
                        'contexts': list({json.dumps(x, sort_keys=True): x for x in contexts}.values()), 'last_reported_token_info': usage,
                        'token_usage_note': 'Last native token_count snapshot only; do not sum across compaction or agents as billing usage.',
                        'tool_counts': dict(tools), 'appliedRuleNames': rules, 'appliedRuleNames_note': 'Field absent when empty; actual system/developer instructions remain in native JSONL and project system-config snapshots.',
                        'markdown': md.relative_to(OUT).as_posix(), 'markdown_sha256': sha(md), 'failure_keyword_native_lines': failures})
    for sid in sorted(registered - set(selected)):
        gaps.append({'session_id': sid, 'reason': 'Registered UUID has no native file.'})
    logfiles = []
    for src in sorted((ROOT / 'logs').rglob('*')):
        if src.is_file():
            target = OUT / 'logs' / src.relative_to(ROOT / 'logs')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            logfiles.append({'source': src.relative_to(ROOT).as_posix(), 'copy': target.relative_to(OUT).as_posix(), 'bytes': src.stat().st_size, 'sha256': sha(src)})
    common = ROOT.parent / 'common/spec-harness'
    harness = {'repository_root': subprocess.check_output(['git', '-C', str(common), 'rev-parse', '--show-toplevel']).decode().strip(),
               'commit': subprocess.check_output(['git', '-C', str(common), 'rev-parse', 'HEAD']).decode().strip(),
               'taskbooks': {p.name: sha(p) for p in sorted(common.glob('[0-3]-*.md'))},
               'local_taskbooks': {p.name: sha(p) for p in sorted((ROOT / 'spec-harness').glob('[0-3]-*.md'))},
               'history': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in sorted((ROOT / 'spec/history').rglob('*')) if p.is_file()]}
    fp = json.loads((ROOT / 'workflow/do-final-fingerprint-02.json').read_text(encoding='utf-8'))
    drift = [x['path'] for x in fp['files'] if not (ROOT / x['path']).is_file() or sha(ROOT / x['path']) != x['sha256']]
    if drift: raise RuntimeError('Production source drift: ' + repr(drift))
    checks = {'checked_at_utc': stamp, 'task_id': 'cml-spec17', 'search': search, 'native_sessions': records,
              'excluded_search_hits': excluded, 'outside_task_search_hit_count': outside_task_hits,
              'outside_task_search_hit_policy': 'Only header used for ownership check; no unrelated UUID, path, prompt or body exported in the search index.',
              'gaps': gaps, 'snapshot_only': True, 'includes_future_events': False,
              'missing_comate_index': not (Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl').exists(),
              'comate_sessionUuid': None, 'comate_sessionUuid_reason': 'This task ran in Codex, not Comate; no Comate engine record exists.',
              'mac_comate_product_exists': Path('/Applications/Comate.app/Contents/Resources/app/product.json').exists(),
              'codex_environment_version': os.environ.get('CODEX_VERSION'),
              'official_baseline_log': {'requested': '../../SWE-OpenHarmony/reports/build-baselines/cml-spec17.log', 'exists': (ROOT / '../../SWE-OpenHarmony/reports/build-baselines/cml-spec17.log').exists(), 'local_evidence': ['logs/prepare-baseline.log', 'logs/baseline-build.log', 'workflow/setup-result.json']},
              'harness': harness, 'production_fingerprint': {'files': len(fp['files']), 'aggregate_sha256': fp['aggregate_sha256'], 'drift': drift}, 'copied_logs': logfiles}
    write(OUT / 'evidence-facts.json', checks)
    (dest / 'code-snapshots').mkdir(parents=True, exist_ok=True)
    (dest / 'code-snapshots/production-final.diff').write_bytes(git('diff', '--binary', '--full-index', fp['base_commit']))
    shutil.copy2(ROOT / 'workflow/do-final-fingerprint-02.json', dest / 'code-snapshots/production-final-fingerprint.json')
    shutil.copy2(ROOT / 'workflow/do-before-implementation.patch', dest / 'code-snapshots/before-implementation.patch')
    write(dest / 'export-manifest.json', {k: checks[k] for k in ('checked_at_utc', 'native_sessions', 'excluded_search_hits', 'gaps', 'snapshot_only', 'includes_future_events')})
    print(json.dumps({'sessions': len(records), 'logs': len(logfiles), 'gaps': gaps, 'production_drift': drift}, ensure_ascii=False))

if __name__ == '__main__':
    main()
