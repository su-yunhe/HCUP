"""Export task-scoped factual evidence; do not edit application inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
NATIVE = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def capture(args, cwd=ROOT):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return {'command': args, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

def cache_reason(rel):
    parts = Path(rel).parts
    if '__pycache__' in parts or str(rel).endswith(('.pyc', '.pyo')):
        return 'reproducible Python bytecode cache'
    if str(rel).replace('\\', '/').startswith('logs/verification-emulator/instances/') and any(
            str(rel).endswith(s) for s in ('.img', '.qcow2', '.lock', '.pid')):
        return 'temporary emulator disk or runtime lock; raw logs retained'
    return None

def main():
    stamp = datetime.now(timezone.utc).isoformat()
    state = json.loads((ROOT / 'workflow/state.json').read_text(encoding='utf-8'))
    excluded = {x['session_id'] for x in state['sessions'] if x.get('excluded_from_task_evidence')}
    sessions = {}
    for row in state['sessions']:
        if row.get('session_id') and row['session_id'] not in excluded:
            sessions.setdefault(row['session_id'], []).append(row)
    queries = {
        'project_path': ['-e', str(ROOT), '-e', str(ROOT).replace('\\', '\\\\'), '-e', ROOT.as_posix()],
        'task_id': ['-e', 'cml-spec7'],
    }
    discoveries, candidate_paths = {}, set()
    for name, terms in queries.items():
        result = capture(['rg', '-l', '-i', '-F', '--glob', '*.jsonl', *terms, str(NATIVE / 'sessions')])
        if result['exit_code'] not in (0, 1):
            raise RuntimeError('Native discovery search failed: ' + str(result))
        paths = result['stdout'].splitlines()
        discoveries[name] = {'query': terms, 'exit_code': result['exit_code'], 'matching_native_files': paths}
        candidate_paths.update(paths)
    discovered_headers = []
    for filename in sorted(candidate_paths):
        if any(sid in Path(filename).name for sid in excluded):
            continue
        with Path(filename).open('r', encoding='utf-8') as handle:
            first = json.loads(handle.readline())
        meta = first.get('payload', {})
        sid = meta.get('id')
        if sid in excluded:
            continue
        relation = meta.get('source', {}).get('subagent', {}).get('thread_spawn', {}) if isinstance(meta.get('source'), dict) else {}
        if Path(meta.get('cwd', '')).resolve() == ROOT.resolve() or relation.get('parent_thread_id') in sessions:
            discovered_headers.append({'id': sid, 'cwd': meta.get('cwd'), 'relation': relation,
                                       'already_registered': sid in sessions})
            sessions.setdefault(sid, [{'role': meta.get('agent_role', 'orchestrator'),
                'agent_id': relation.get('agent_path', 'root'), 'session_id': sid,
                'registration_note': 'Discovered from actual native header; not a synthesized workflow registration'}])
    index = NATIVE / 'session_index.jsonl'
    matched_root, matched_task = [], []
    if index.exists():
        for line in index.read_text(encoding='utf-8').splitlines():
            # Matching first: never export unrelated private rows.
            if 'cml-spec7' in line:
                x = json.loads(line)
                if x.get('id') not in excluded:
                    matched_task.append(x)
            if str(ROOT).casefold() in line.casefold() or ROOT.as_posix().casefold() in line.casefold():
                x = json.loads(line)
                if x.get('id') not in excluded:
                    matched_root.append(x)
    selected = []
    gaps = []
    raw_rows = []
    tools_seen = Counter()
    skills_seen = Counter()
    for sid, registrations in sorted(sessions.items()):
        found = list((NATIVE / 'sessions').rglob('*-' + sid + '.jsonl'))
        if not found:
            gaps.append('Missing native rollout for registered session ' + sid)
            continue
        src = found[0]
        raw = src.read_bytes()
        lines = raw.decode('utf-8').splitlines()
        header = json.loads(lines[0])['payload']
        if header.get('id') != sid:
            raise ValueError('Session metadata mismatch: ' + sid)
        parent_relation = header.get('source', {}).get('subagent', {}).get('thread_spawn', {}) if isinstance(header.get('source'), dict) else {}
        if Path(header['cwd']).resolve() != ROOT.resolve() and parent_relation.get('parent_thread_id') not in sessions:
            raise ValueError('Session cwd outside task: ' + sid)
        target = OUT / 'traces/native' / (sid + '.jsonl')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        models, contexts, token, latest_usage, kinds = [], [], None, None, Counter()
        md = ['# Native JSONL readable copy: ' + sid, '',
              'Generated mechanically from the adjacent native file; not an IDE Markdown export.', '',
              'Each heading gives the original JSONL line number. Complete event objects, including failed tool results, follow.', '']
        parse_errors = []
        for n, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as err:
                parse_errors.append({'line': n, 'error': str(err)})
                md.extend([f'## Line {n}: unparsed native bytes', '```text', line, '```', ''])
                continue
            typ, p = obj.get('type'), obj.get('payload', {})
            kinds[typ] += 1
            if typ == 'turn_context':
                c = {k: p[k] for k in ['model', 'effort', 'cwd', 'approval_policy', 'sandbox_policy'] if k in p}
                if c not in contexts:
                    contexts.append(c)
                if p.get('model') and p['model'] not in models:
                    models.append(p['model'])
            if typ == 'event_msg' and p.get('type') == 'token_count':
                token = p.get('info')
            if typ == 'token_usage_record':
                latest_usage = {'source_line': n, **p}
            if typ == 'response_item' and p.get('type') in ('function_call', 'custom_tool_call'):
                tools_seen[p.get('name', '')] += 1
                args = p.get('arguments', p.get('input', ''))
                for name in ['harmony-task-flow', 'hmos-arkts-syntax-checker', 'hmos-arkts-knowledge-retriever', 'arkts-syntax-assistant']:
                    if name in str(args):
                        skills_seen[name] += 1
            md.extend([f'## Line {n}: {typ}', '```json', json.dumps(obj, ensure_ascii=False, indent=2), '```', ''])
        (OUT / 'traces/markdown').mkdir(exist_ok=True)
        (OUT / 'traces/markdown' / (sid + '.md')).write_text('\n'.join(md), encoding='utf-8')
        sidebar = []
        for x in matched_task + matched_root:
            if x.get('id') == sid and x not in sidebar:
                sidebar.append(x)
        row = {'session_id': sid, 'Comate_sessionUuid': '【待补充】（当前使用Codex，未发现Comate记录）',
               'Codex_native_session_id': sid, 'IDE_sidebar_id': sid if sidebar else '【待补充】（未找到该原生线程的侧边栏索引行）',
               'sidebar_index_rows': sidebar, 'agent_registrations': registrations,
               'native_path': target.relative_to(OUT).as_posix(), 'markdown_path': 'traces/markdown/' + sid + '.md',
               'source_path': str(src), 'source_header_cwd': header['cwd'],
               'source_session_meta_line': 1, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
               'source_header_session_id': header.get('session_id'),
               'parent_thread_relation': header.get('source', {}).get('subagent', {}).get('thread_spawn') if isinstance(header.get('source'), dict) else None,
               'ends_with_newline': raw.endswith(b'\n'), 'parse_errors': parse_errors,
               'cli_version': header.get('cli_version', '【待补充】'), 'originator': header.get('originator'),
               'source': header.get('source'), 'thread_source': header.get('thread_source'),
               'agent_nickname': header.get('agent_nickname'), 'agent_role': header.get('agent_role'),
               'models': models, 'turn_contexts': contexts, 'latest_token_info': token,
               'latest_token_usage_record': latest_usage,
               'event_counts': dict(kinds), 'exported_at_utc': stamp,
               'snapshot_only': True, 'includes_future_events': False}
        selected.append(row)
    relevant_ids = set(sessions)
    for row in matched_task + matched_root:
        if row.get('id') in relevant_ids and row not in raw_rows:
            raw_rows.append(row)
    dst_index = OUT / 'traces/session-index.filtered.jsonl'
    dst_index.parent.mkdir(parents=True, exist_ok=True)
    dst_index.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in raw_rows), encoding='utf-8')
    # A second dimension is independently checked against native cwd, as the sidebar index has no cwd column.
    write(OUT / 'traces/discovery.json', {
        'searched_at_utc': stamp, 'Comate_index': str(Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl'),
        'Comate_index_exists': (Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl').exists(),
        'project_dimension': {'query': str(ROOT), 'native_session_meta_cwd_matches': [x['session_id'] for x in selected],
                              'sidebar_index_path_matches': matched_root, 'note': 'Codex sidebar index has titles/IDs, not workspace columns; each registered native header cwd checked.'},
        'task_dimension': {'query': 'cml-spec7', 'sidebar_index_matches': matched_task},
        'excluded_overview_session_ids': sorted(excluded), 'excluded_reason': 'AGENTS.md forbids mixed initialization overview as development evidence',
        'no_entire_client_database_exported': True, 'missing': gaps})
    write(OUT / 'traces/native-discovery-search.json', {'queries': discoveries, 'selected_headers': discovered_headers,
          'excluded_session_ids': sorted(excluded), 'note': 'Two independent rg searches; only selected task header/parent matches are exported. Unrelated matching bodies are not loaded or exported.'})
    session_map = ['# Actual native/sidebar session mapping', '',
        'Codex native thread identity is session_meta.payload.id. The payload.session_id may be the parent engine session for a subagent.',
        'Comate sessionUuid is not present. No fabricated Comate identifiers are supplied. Sidebar IDs below come from the filtered original Codex session index.', '',
        '| Native thread ID | Sidebar ID | Parent native thread | Role | Native file |',
        '| --- | --- | --- | --- | --- |']
    for row in selected:
        parent=(row.get('parent_thread_relation') or {}).get('parent_thread_id', '')
        roles=', '.join(sorted({x.get('role','') for x in row['agent_registrations']}))
        session_map.append(f"| {row['session_id']} | {row['IDE_sidebar_id']} | {parent} | {roles} | {row['native_path']} |")
    (OUT/'traces/session-map.md').write_text('\n'.join(session_map)+'\n',encoding='utf-8')
    write(OUT / 'traces/session-metadata.json', {'exported_at_utc': stamp, 'sessions': selected, 'gaps': gaps,
          'token_note': 'Latest native token_count.info per session; snapshots are partial for active sessions. Do not add repeated cumulative events or infer missing Comate tokenUsage.',
          'tools_observed': dict(tools_seen), 'skill_name_occurrences_in_tool_arguments': dict(skills_seen)})
    copied, omitted = [], []
    for p in sorted((ROOT / 'logs').rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        why = cache_reason(rel)
        item = {'path': rel, 'bytes': p.stat().st_size, 'sha256': digest(p)}
        if why:
            omitted.append({**item, 'reason': why})
            continue
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or digest(dest) != item['sha256']:
            shutil.copyfile(p, dest)
        copied.append(item)
    write(OUT / 'logs-copy-manifest.json', {'copied': copied, 'excluded_reproducible_cache': omitted,
          'note': 'No original files deleted or modified. Failure/retry/device logs retained. Temporary simulator virtual disks and bytecode are excluded from submission snapshot.'})
    versions = {}
    common = ROOT.parent / 'common/spec-harness'
    common_head = capture(['git', '-C', str(common), 'rev-parse', 'HEAD'])
    versions['common_containing_git_head'] = common_head
    versions['common_actual_git_root'] = capture(['git', '-C', str(common), 'rev-parse', '--show-toplevel'])
    versions['task_books'] = [{'common_path': '../common/spec-harness/' + n, 'sha256': digest(common / n),
                               'local_path': 'spec-harness/' + n, 'local_sha256': digest(ROOT / 'spec-harness' / n)}
                              for n in ['0-analyze.md', '1-do.md', '2-submit.md', '3-package.md']]
    versions['history'] = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)} for p in sorted((ROOT/'spec/history').rglob('*')) if p.is_file()]
    versions['official_templates'] = [{'path': str(p), 'sha256': digest(p)} for p in [Path('D:/SWE-OpenHarmony/templates') / n for n in ['submission-checklist.md', 'trace-index.md', 'submission.json']]]
    versions['official_baseline_report'] = {'path': 'D:/SWE-OpenHarmony/reports/build-baselines/cml-spec7.log', 'exists': Path('D:/SWE-OpenHarmony/reports/build-baselines/cml-spec7.log').exists(),
                                            'substitute_existing_task_evidence': 'logs/prepare-baseline.log; logs/baseline-build.log; workflow/baseline-provenance.json'}
    write(OUT / 'taskbook-versions.json', versions)
    for name, source in [('team.yaml', common/'team.yaml'), ('submit-input.yaml', ROOT/'spec/submit-input.yaml')]:
        target = OUT/'evidence-inputs'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    for row in versions['official_templates']:
        source=Path(row['path'])
        target=OUT/'evidence-inputs/templates'/source.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    config_sources = [Path('D:/HarmonyDev/codex/skills/harmony-task-flow')/name for name in
        ['SKILL.md','references/local-setup.md','references/protocol.md','references/traces.md','scripts/workflow.py']]
    config_sources += [Path('D:/HarmonyDev/codex/agents')/('harmony_'+name+'.toml') for name in
        ['requirements','design','implementation','verification']]
    config_rows=[]
    for source in config_sources:
        target=OUT/'evidence-inputs/current-config'/source.relative_to(Path('D:/HarmonyDev/codex'))
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        config_rows.append({'source_path':str(source),'copy':target.relative_to(OUT).as_posix(),'sha256':digest(source)})
    write(OUT/'evidence-inputs/current-config/manifest.json',config_rows)
    hap = ROOT / 'entry/build/default/outputs/default/entry-default-unsigned.hap'
    app = capture(['powershell', '-NoProfile', '-Command', "Get-AppxPackage -Name OpenAI.Codex | Select-Object Name,Version,InstallLocation | ConvertTo-Json -Compress"])
    facts = {'collected_at_utc': stamp, 'task_id': 'cml-spec7',
             'base_commit': json.loads((ROOT/'spec/metadata.json').read_text())['base_commit'],
             'git_head': capture(['git','rev-parse','HEAD'])['stdout'].strip(),
             'app_package': app, 'Comate_client_version': '【待补充】（Comate未使用或未发现）',
             'Comate_extension_version': '【待补充】（无对应扩展记录）',
             'hap': {'path': hap.relative_to(ROOT).as_posix(), 'exists': hap.exists(),
                     'bytes': hap.stat().st_size if hap.exists() else None, 'sha256': digest(hap) if hap.exists() else None},
             'validation': state.get('implementation_validation'), 'original_record_gaps': state.get('record_gaps', [])}
    write(OUT / 'facts.json', facts)
    print(json.dumps({'sessions': len(selected), 'gaps': gaps, 'logs': len(copied), 'cache_exclusions': len(omitted), 'hap': facts['hap']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
