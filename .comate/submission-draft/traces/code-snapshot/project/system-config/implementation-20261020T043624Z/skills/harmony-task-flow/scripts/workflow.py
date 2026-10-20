"""Local, single-writer checkpoints for the Harmony Cup coordinator (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from uuid import UUID, uuid4

PHASES = ('setup', 'requirements', 'design', 'implementation', 'verification', 'acceptance')
STATUSES = ('in_progress', 'waiting_user', 'blocked', 'local_validation_complete')
ROLES = ('orchestrator', 'harmony_requirements', 'harmony_design',
         'harmony_implementation', 'harmony_verification')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp-' + uuid4().hex)
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def load_state(root):
    state = json.loads((root / 'workflow/state.json').read_text(encoding='utf-8'))
    if Path(state['root']).resolve() != root:
        raise ValueError('Task root differs from stored state; migrate explicitly, do not silently reset.')
    return state


def append_event(root, state, event):
    event = {'time': now(), 'event_id': uuid4().hex, **event}
    with (root / 'workflow/events.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + '\n')
    state['updated_at'] = event['time']
    state['last_event_id'] = event['event_id']
    write_json(root / 'workflow/state.json', state)


def normalize_session(value):
    return str(UUID(value)) if value else None


def initialize(args):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.task):
        raise ValueError('Task ID must contain lowercase letters, numbers and single hyphens.')
    root = Path(args.root).resolve()
    spec, metadata_path = Path(args.spec).resolve(), Path(args.metadata).resolve()
    metadata = json.loads(metadata_path.read_text(encoding='utf-8-sig'))
    commit = metadata.get('base_commit', '')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('metadata.base_commit must be a full 40-character SHA.')
    bundle = metadata.get('baseline_bundle', '')
    parts = PurePosixPath(bundle)
    if (parts.is_absolute() or '\\' in bundle or '..' in parts.parts
            or len(parts.parts) != 2 or parts.parts[0] != 'repo_bundles'
            or not bundle.endswith('.bundle')):
        raise ValueError('metadata.baseline_bundle must name one file under repo_bundles/.')
    hashes = {'spec_sha256': digest(spec), 'metadata_sha256': digest(metadata_path)}
    if (root / 'workflow/state.json').exists():
        state = load_state(root)
        if state['task_id'] != args.task or any(state[k] != v for k, v in hashes.items()):
            raise ValueError('Existing task or input hashes differ; refusing to overwrite.')
        if digest(root / 'inputs/Spec.md') != hashes['spec_sha256']:
            raise ValueError('Saved Spec has changed; investigate before resuming.')
        if digest(root / 'inputs/metadata.json') != hashes['metadata_sha256']:
            raise ValueError('Saved metadata has changed; investigate before resuming.')
        return {'action': 'resume', 'state': str(root / 'workflow/state.json'), 'phase': state['phase']}
    if root.exists() and any(root.iterdir()):
        raise ValueError('Destination is nonempty without workflow state; inspect and adopt explicitly.')
    for directory in ('inputs', 'workflow', 'workflow/requirements', 'workflow/design',
                      'workflow/implementation', 'workflow/verification', 'traces', 'system-config'):
        (root / directory).mkdir(parents=True, exist_ok=True)
    shutil.copy2(spec, root / 'inputs/Spec.md')
    shutil.copy2(metadata_path, root / 'inputs/metadata.json')
    skill = Path(__file__).resolve().parent.parent
    agents = skill.parent.parent / 'agents'
    snapshot = root / 'system-config' / ('initial-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    shutil.copytree(skill, snapshot / 'skills' / 'harmony-task-flow', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (snapshot / 'agents').mkdir()
    for role in ROLES[1:]:
        shutil.copy2(agents / (role + '.toml'), snapshot / 'agents' / (role + '.toml'))
    parent_session = normalize_session(os.environ.get('CODEX_THREAD_ID'))
    state = {
        'schema_version': 1, 'task_id': args.task, 'root': str(root),
        'project': str(root / 'project'), 'base_commit': commit, 'baseline_bundle': bundle,
        **hashes, 'phase': 'setup', 'status': 'in_progress', 'created_at': now(),
        'sessions': ([{'role': 'orchestrator', 'agent_id': 'root', 'session_id': parent_session,
                      'registered_at': now()}] if parent_session else []),
        'approved_artifacts': {}, 'code_fingerprint': None, 'failures': [], 'open_questions': [],
        'next_action': 'Prepare the selected baseline, preserve its output, then dispatch requirements.',
        'config_snapshot': str(snapshot.relative_to(root)),
        'record_gaps': ['Native session snapshots have not yet been collected.'],
    }
    guidance = (
        '# 本题自动调度\n\n'
        f'题号：{args.task}\n\n本题根目录：{root.as_posix()}\n\n'
        f'主 Agent 开始/继续作答时加载 `{(skill / "SKILL.md").as_posix()}`，'
        '读取 workflow/state.json，调度四个角色并按失败证据回退。\n\n'
        '子 Agent 仅完成收到的派工，不自行成为调度者或创建子 Agent。'
        '仅使用本题 inputs、project 和记录；禁止其他题工程及相关上游修复历史。\n'
    )
    (root / 'AGENTS.md').write_text(guidance, encoding='utf-8')
    append_event(root, state, {'type': 'initialize', 'task_id': args.task, 'input_hashes': hashes})
    return {'action': 'initialized', 'state': str(root / 'workflow/state.json'), 'project_created': False}


def record(args):
    root = Path(args.root).resolve()
    state = load_state(root)
    evidence = []
    for item in args.evidence:
        path = (root / item).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Evidence must be an existing file inside this task: ' + item)
        evidence.append({'path': path.relative_to(root).as_posix(), 'sha256': digest(path)})
    if args.status == 'local_validation_complete' and (args.phase != 'acceptance' or not evidence):
        raise ValueError('Completion requires phase acceptance and existing acceptance evidence.')
    previous = {'phase': state['phase'], 'status': state['status']}
    state.update(phase=args.phase, status=args.status, next_action=args.next_action)
    append_event(root, state, {'type': 'route', 'from': previous, 'phase': args.phase,
                             'status': args.status, 'reason': args.reason,
                             'next_action': args.next_action, 'evidence': evidence})
    return {'phase': state['phase'], 'status': state['status']}


def session(args):
    root = Path(args.root).resolve()
    state = load_state(root)
    item = {'role': args.role, 'agent_id': args.agent_id,
            'session_id': normalize_session(args.session_id), 'registered_at': now()}
    matches = [entry for entry in state['sessions'] if entry['agent_id'] == args.agent_id
               and entry['role'] == args.role]
    if matches and matches[-1].get('session_id') == item['session_id']:
        return {'action': 'already_registered', 'role': args.role}
    # Keep previous assignments for audit; snapshot collection de-duplicates UUIDs.
    state['sessions'].append(item)
    append_event(root, state, {'type': 'session_registered', 'session': item})
    return {'action': 'registered', 'role': args.role}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    for arg in ('task', 'root', 'spec', 'metadata'):
        init.add_argument('--' + arg, required=True)
    init.set_defaults(run=initialize)
    event = commands.add_parser('event')
    event.add_argument('--root', required=True)
    event.add_argument('--phase', required=True, choices=PHASES)
    event.add_argument('--status', default='in_progress', choices=STATUSES)
    event.add_argument('--reason', required=True)
    event.add_argument('--next-action', required=True)
    event.add_argument('--evidence', action='append', default=[])
    event.set_defaults(run=record)
    register = commands.add_parser('session')
    register.add_argument('--root', required=True)
    register.add_argument('--role', required=True, choices=ROLES)
    register.add_argument('--agent-id', required=True)
    register.add_argument('--session-id')
    register.set_defaults(run=session)
    args = parser.parse_args()
    try:
        print(json.dumps(args.run(args), ensure_ascii=False))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
