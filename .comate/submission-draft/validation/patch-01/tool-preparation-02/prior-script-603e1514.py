#!/usr/bin/env python3
"""Freeze this task's material scope and prove its binary patch reconstructs it.

No build/device/network commands. The real repository index/HEAD are read-only.
Run --help freely. --execute is intended only after the orchestrator's explicit GO.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import time
import traceback

TASK = 'cml-spec28'
BASE = '9a1d608dc89acfc301657c33ce5dd6089cbf9572'
INIT_UUID = '01a13fc4-2611-7761-a580-1283e0c70541'
DRAFT = '.comate/submission-draft'
DERIVED_FILES = {
    f'{DRAFT}/changes/final.diff',
    f'{DRAFT}/changes/project-files.json',
    f'{DRAFT}/changes/excluded-files.json',
}
DERIVED_PREFIXES = (f'{DRAFT}/validation/', f'{DRAFT}/traces/materials-final/')
LIVE_PREFIX = 'traces/analysis/baseline-runtime/emulator-instances/'
CACHE_PARTS = {
    '.git', 'node_modules', 'oh_modules', 'build', '.hvigor', '__pycache__',
    'venv', '.venv', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache',
    'caches', '.cxx', '.test', '.appanalyzer',
}
BINARY_SUFFIXES = {
    '.hap', '.har', '.app', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp',
    '.ico', '.pdf', '.sqlite', '.sqlite3', '.db', '.zip', '.7z', '.gz', '.tar',
    '.woff', '.woff2', '.ttf', '.otf', '.so', '.dll', '.exe', '.bin', '.mp4',
    '.p12', '.pfx', '.cer', '.der',
}
utc = lambda: dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path: pathlib.Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size


def dump(path: pathlib.Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def assert_inside(path: pathlib.Path, parent: pathlib.Path) -> pathlib.Path:
    resolved = path.resolve()
    resolved.relative_to(parent.resolve())
    return resolved


def no_links(path: pathlib.Path, parent: pathlib.Path, allow_missing: bool = False) -> None:
    """Check every existing component before reading; reject even in-scope links."""
    absolute = pathlib.Path(os.path.abspath(path))
    relative = absolute.relative_to(pathlib.Path(os.path.abspath(parent)))
    cursor = pathlib.Path(os.path.abspath(parent))
    for component in relative.parts:
        cursor /= component
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            if allow_missing:
                break
            raise
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
            raise RuntimeError(f'Link/reparse point rejected without following it: {cursor}')
    assert_inside(absolute, parent)


def safe_rel(value: str) -> str:
    value = value.replace('\\', '/')
    p = pathlib.PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or not p.parts or ':' in value or '\x00' in value:
        raise RuntimeError(f'Unsafe repository path: {value!r}')
    return p.as_posix()


def exclusion(rel: str) -> str | None:
    lower = rel.casefold()
    name = pathlib.PurePosixPath(rel).name
    # This condition is evaluated by filename alone, before stat/hash/content.
    if INIT_UUID in name and name.casefold().endswith('.jsonl'):
        return 'shared initialization overview native raw: filename-only exclusion; body never read'
    if rel in DERIVED_FILES:
        return 'explicit self-referential derived material'
    if any(rel.startswith(prefix) for prefix in DERIVED_PREFIXES):
        return 'explicit derived validation or post-freeze material traces'
    if rel.startswith(LIVE_PREFIX):
        return 'active emulator instance/live disk scope excluded without reading contents'
    if any(part.casefold() in CACHE_PARTS for part in pathlib.PurePosixPath(rel).parts):
        return 'dependency/build/runtime cache or Git metadata component'
    if lower.endswith(('-shm', '-journal')) or lower.endswith(('.sqlite-journal', '.db-journal')):
        return 'SQLite SHM/temporary journal sidecar; nonempty stopped WAL is handled separately with its main DB'
    if lower.endswith(('.pyc', '.pyo')):
        return 'Python bytecode cache'
    return None


class Freeze:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.root = pathlib.Path(args.root).resolve()
        self.draft = self.root / DRAFT
        self.validation = self.draft / 'validation/patch-01'
        self.run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', self.run_id):
            raise RuntimeError('run-id must be a single safe directory component')
        self.run = self.validation / self.run_id
        no_links(self.validation, self.root, allow_missing=True)
        assert_inside(self.run, self.validation)
        if self.run.exists():
            raise RuntimeError('Existing run is never overwritten: ' + str(self.run))
        self.run.mkdir(parents=True, exist_ok=False)
        self.commands: list[dict] = []
        self.phase = 'initialization'
        self.result = {
            'schema_version': 1, 'task_id': TASK, 'run_id': self.run_id,
            'started_at_utc': utc(), 'status': 'running', 'root': str(self.root),
            'run_directory': self.rel(self.run), 'commands': self.commands,
            'scope': 'Material freeze / local binary patch reconstruction only; no build, device, server or external fetch',
            'explicit_GO_must_precede_execution': True,
            'derivative_exceptions_are_not_claimed_as_no_exceptions': True,
        }
        self.empty_hooks = self.run / 'empty-hooks'
        self.empty_hooks.mkdir()
        self.env = os.environ.copy()
        self.env.update({
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_ATTR_NOSYSTEM': '1', 'GIT_LFS_SKIP_SMUDGE': '1',
            'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0',
            'GIT_TEMPLATE_DIR': str(self.empty_hooks),
        })
        # Do not inherit a caller's alternate index/worktree/object directories.
        for key in ('GIT_INDEX_FILE', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR',
                    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                    'GIT_CONFIG_COUNT', 'GIT_CONFIG_PARAMETERS'):
            self.env.pop(key, None)
        for key in list(self.env):
            if key.startswith(('GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')):
                self.env.pop(key)
        self.git_options = [
            '-c', 'core.autocrlf=false', '-c', 'core.safecrlf=false',
            '-c', 'core.longpaths=true',
            '-c', 'core.symlinks=false', '-c', 'core.fsmonitor=false',
            '-c', f'core.hooksPath={self.empty_hooks}',
            '-c', 'filter.lfs.process=', '-c', 'filter.lfs.smudge=',
            '-c', 'filter.lfs.required=false', '-c', 'protocol.allow=never',
            '-c', 'protocol.file.allow=always', '-c', 'submodule.recurse=false',
        ]

    def rel(self, path: pathlib.Path) -> str:
        return path.relative_to(self.root).as_posix()

    def command(self, args: list[str], cwd: pathlib.Path | None = None,
                stdin: bytes | None = None, require_ok: bool = True) -> pathlib.Path:
        sequence = len(self.commands) + 1
        base = self.run / 'commands' / f'{sequence:03d}'
        base.parent.mkdir(exist_ok=True)
        output, error = base.with_suffix('.stdout'), base.with_suffix('.stderr')
        entry = {'sequence': sequence, 'phase': self.phase, 'argv': args,
                 'cwd': str(cwd or self.root), 'started_at_utc': utc(),
                 'stdout': self.rel(output), 'stderr': self.rel(error),
                 'stdin_bytes': len(stdin) if stdin is not None else 0,
                 'stdin_sha256': hashlib.sha256(stdin).hexdigest() if stdin is not None else None}
        self.commands.append(entry)
        start = time.monotonic()
        try:
            with output.open('wb') as out, error.open('wb') as err:
                proc = subprocess.run(args, cwd=cwd or self.root, env=self.env,
                                      input=stdin, stdout=out, stderr=err, check=False)
            entry['exit_code'] = proc.returncode
        except BaseException as exc:
            entry['exception'] = type(exc).__name__ + ': ' + str(exc)
            raise
        finally:
            entry['finished_at_utc'] = utc()
            entry['elapsed_seconds'] = time.monotonic() - start
            for label, path in [('stdout', output), ('stderr', error)]:
                if path.exists():
                    h, size = digest(path)
                    entry[label+'_sha256'], entry[label+'_bytes'] = h, size
            dump(base.with_suffix('.json'), entry)
            dump(self.run/'commands.json', self.commands)
        if require_ok and entry['exit_code'] != 0:
            raise RuntimeError(f'Command {sequence} failed with exit {entry["exit_code"]}; original stdout/stderr retained')
        return output

    def git(self, args: list[str], cwd: pathlib.Path | None = None,
            stdin: bytes | None = None, require_ok: bool = True) -> pathlib.Path:
        return self.command(['git', *self.git_options, *args], cwd, stdin, require_ok)

    def original_state(self) -> dict:
        head = self.git(['rev-parse', 'HEAD']).read_text(encoding='utf-8').strip()
        gitdir = pathlib.Path(self.git(['rev-parse', '--absolute-git-dir']).read_text(encoding='utf-8').strip())
        no_links(gitdir, self.root)
        index = gitdir / 'index'
        no_links(index, self.root)
        h, size = digest(index)
        return {'HEAD': head, 'index_path': str(index), 'index_sha256': h, 'index_bytes': size}

    def formal_check(self) -> dict:
        manifest_path = self.root / safe_rel(self.args.formal_manifest)
        no_links(manifest_path, self.root)
        data = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        if data.get('count') != 827 or len(data.get('files', [])) != 827:
            raise RuntimeError('Formal source manifest must contain the approved 827 files')
        differences = []
        for item in data['files']:
            rel = safe_rel(item['path'])
            path = self.root / rel
            no_links(path, self.root)
            actual, size = digest(path)
            if actual != item['sha256']:
                differences.append({'path': rel, 'expected': item['sha256'], 'actual': actual})
        hap = self.root / safe_rel(self.args.formal_hap)
        no_links(hap, self.root)
        hap_sha, hap_size = digest(hap)
        check = {'manifest': self.args.formal_manifest, 'manifest_sha256': digest(manifest_path)[0],
                 'declared_source_aggregate': data.get('aggregate'), 'checked_files': 827,
                 'differences': differences, 'hap_path': self.args.formal_hap,
                 'hap_sha256': hap_sha, 'hap_bytes': hap_size,
                 'expected_hap_sha256': self.args.expected_hap_sha256,
                 'source_equal': not differences,
                 'hap_equal': hap_sha == self.args.expected_hap_sha256, 'at_utc': utc()}
        if not check['source_equal'] or not check['hap_equal']:
            self.result.setdefault('formal_checks_failed', []).append(check)
            raise RuntimeError('Approved formal source/HAP consistency failed')
        return check

    def inventory(self) -> tuple[dict[str, list[str]], list[dict]]:
        groups = [('tracked', ['ls-files', '-z']),
                  ('normal-untracked', ['ls-files', '--others', '--exclude-standard', '-z'])]
        candidates: dict[str, list[str]] = {}
        for label, args in groups:
            raw = self.git(args).read_bytes()
            for name in raw.split(b'\0'):
                if name:
                    rel = safe_rel(os.fsdecode(name))
                    candidates.setdefault(rel, []).append(label)
        candidates.setdefault('AGENTS.md', []).append('explicit-required-AGENTS')
        excluded = []
        included = {}
        for rel, origins in sorted(candidates.items()):
            reason = exclusion(rel)
            if reason:
                excluded.append({'path': rel, 'origins': origins, 'reason': reason})
                continue
            path = self.root / rel
            # Missing tracked entries still participate in base-to-final deletions.
            if not path.exists() and not path.is_symlink():
                excluded.append({'path': rel, 'origins': origins,
                                 'reason': 'currently absent tracked/candidate path; omitted from final, deletion retained in patch'})
                continue
            no_links(path, self.root)
            if not path.is_file():
                raise RuntimeError('Non-regular candidate (including submodule) needs explicit disposition: '+rel)
            if rel.casefold().endswith('-wal'):
                if path.stat().st_size == 0:
                    excluded.append({'path': rel, 'origins': origins, 'reason': 'empty stopped SQLite WAL'})
                    continue
                main = self.root/rel[:-4]
                no_links(main, self.root)
                if not main.is_file():
                    raise RuntimeError('Nonempty WAL without its main DB: '+rel)
                origins = origins + ['nonempty-stopped-WAL-paired-original-evidence']
            included[rel] = origins
        for rel in included:
            if rel.casefold().endswith('-wal') and rel[:-4] not in included:
                raise RuntimeError('Nonempty WAL main DB was excluded from frozen scope: '+rel)
        # List ignored files/directories without opening or recursively enumerating their contents.
        ignored = self.git(['ls-files', '--others', '--ignored', '--exclude-standard', '--directory', '-z']).read_bytes()
        for name in ignored.split(b'\0'):
            if name:
                rel = safe_rel(os.fsdecode(name))
                if rel == 'AGENTS.md':
                    continue
                excluded.append({'path': rel, 'origins': ['git-ignored-not-candidate'],
                                 'reason': 'not in normal-untracked candidate set; '+(exclusion(rel) or 'Git ignore rule'),
                                 'directory_prefix': os.fsdecode(name).endswith('/')})
        return included, excluded

    def base_tree(self) -> dict[str, dict]:
        raw = self.git(['ls-tree', '-rz', '--full-tree', BASE]).read_bytes()
        tree = {}
        for item in raw.split(b'\0'):
            if item:
                head, name = item.split(b'\t', 1)
                mode, kind, oid = head.decode('ascii').split()
                tree[safe_rel(os.fsdecode(name))] = {'mode': mode, 'type': kind, 'object_id': oid}
        return tree

    def preserve_prior(self, path: pathlib.Path) -> None:
        no_links(path, self.root, allow_missing=True)
        if path.exists():
            target = self.run / 'prior-canonical-artifacts' / path.name
            if target.exists():
                raise RuntimeError('Prior artifact backup collision')
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, target)
            self.result.setdefault('preserved_prior_artifacts', []).append({
                'original': self.rel(path), 'backup': self.rel(target), 'sha256': digest(target)[0]})

    def safe_db(self, path: pathlib.Path) -> None:
        if path.suffix.casefold() not in {'.sqlite', '.sqlite3', '.db'}:
            return
        for suffix in ('-wal', '-journal'):
            sidecar = pathlib.Path(str(path)+suffix)
            no_links(sidecar, self.root, allow_missing=True)
            if suffix == '-journal' and sidecar.exists() and sidecar.stat().st_size:
                raise RuntimeError('Database has a nonempty live/temporary sidecar; do not omit committed data: '+self.rel(sidecar))

    def hash_entries(self, paths: dict[str, list[str]]) -> list[dict]:
        entries = []
        for rel, origins in sorted(paths.items()):
            path = self.root / rel
            no_links(path, self.root)
            self.safe_db(path)
            before = path.stat()
            h, size = digest(path)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise RuntimeError('File changed while freezing: '+rel)
            entries.append({'path': rel, 'bytes': size, 'sha256': h, 'mtime_ns_at_capture': after.st_mtime_ns, 'origins': origins})
        return entries

    def audit_databases(self, entries: list[dict]) -> None:
        """SQLite may change only disposable audit copies, never original/canonical trees."""
        wanted = {e['path']: e for e in entries}
        audits = []
        self.result['sqlite_audits'] = audits
        for item in entries:
            rel = item['path']
            source = self.root/rel
            if source.suffix.casefold() not in {'.sqlite', '.sqlite3', '.db'}:
                continue
            folder = self.run/'sqlite-audit'/f'{len(audits)+1:03d}'
            no_links(folder, self.validation, allow_missing=True)
            folder.mkdir(parents=True, exist_ok=False)
            target = folder/source.name
            pair = [item]
            wal = wanted.get(rel+'-wal')
            if wal:
                pair.append(wal)
            audit = {'source_db': rel, 'source_wal': wal['path'] if wal else None,
                     'audit_directory': self.rel(folder), 'started_at_utc': utc(),
                     'SQLite_version': sqlite3.sqlite_version,
                     'operation': 'Open disposable audit DB+WAL copy; PRAGMA integrity_check; close. No original DB/engineering-copy checkpoint or connection.',
                     'copied_files': []}
            audits.append(audit)
            try:
                for member in pair:
                    original = self.root/member['path']
                    no_links(original, self.root)
                    before = original.stat()
                    if before.st_mtime_ns != member['mtime_ns_at_capture']:
                        raise RuntimeError('DB/WAL mtime changed before audit copy: '+member['path'])
                    copied = folder/original.name
                    shutil.copyfile(original, copied)
                    h, size = digest(copied)
                    original_h, original_size = digest(original)
                    after = original.stat()
                    equal = h == original_h == member['sha256'] and size == original_size == member['bytes'] and before.st_mtime_ns == after.st_mtime_ns
                    audit['copied_files'].append({'path': member['path'], 'audit_copy': self.rel(copied),
                                                  'expected_sha256': member['sha256'], 'copy_sha256': h,
                                                  'original_postcopy_sha256': original_h,
                                                  'original_mtime_ns_before': before.st_mtime_ns,
                                                  'original_mtime_ns_after': after.st_mtime_ns,
                                                  'stable_and_equal': equal})
                    if not equal:
                        raise RuntimeError('DB/WAL source/copy is not stable: '+member['path'])
                connection = sqlite3.connect(str(target), timeout=5)
                try:
                    audit['journal_mode_on_audit_copy'] = connection.execute('PRAGMA journal_mode').fetchall()
                    audit['integrity_check_rows'] = connection.execute('PRAGMA integrity_check').fetchall()
                finally:
                    connection.close()
                audit['integrity_ok'] = audit['integrity_check_rows'] == [('ok',)]
                if not audit['integrity_ok']:
                    raise RuntimeError('SQLite integrity_check failed on disposable copy: '+rel)
            except BaseException as exc:
                audit['error'] = type(exc).__name__+': '+str(exc)
                raise
            finally:
                audit['finished_at_utc'] = utc()
                dump(folder/'audit.json', audit)

    def make_binary_manifest(self, candidates: dict[str, list[str]], tree: dict) -> None:
        items = []
        object_ids = []
        for rel in sorted(candidates):
            path = self.root / rel
            no_links(path, self.root)
            self.safe_db(path)
            with path.open('rb') as stream:
                head = stream.read(8192)
            try:
                head.decode('utf-8')
                non_utf8 = False
            except UnicodeDecodeError:
                non_utf8 = True
            if path.suffix.casefold() not in BINARY_SUFFIXES and b'\0' not in head and not non_utf8:
                continue
            h, size = digest(path)
            baseline = tree.get(rel)
            entry = {'path': rel, 'bytes': size, 'sha256': h,
                     'classification': 'known binary suffix, NUL byte, or non-UTF8 prefix',
                     'baseline_path_present': baseline is not None,
                     'baseline_tree_entry': baseline, 'baseline_identical_bytes': False}
            items.append(entry)
            if baseline and baseline['type'] == 'blob':
                object_ids.append(baseline['object_id'])
        blobs = {}
        if object_ids:
            ids = sorted(set(object_ids))
            output = self.git(['cat-file', '--batch'], stdin=('\n'.join(ids)+'\n').encode('ascii'))
            with output.open('rb') as stream:
                for requested in ids:
                    header = stream.readline().decode('ascii').rstrip('\n')
                    oid, kind, size_string = header.split()
                    if oid != requested or kind != 'blob':
                        raise RuntimeError('Unexpected baseline cat-file response')
                    remaining = int(size_string)
                    h = hashlib.sha256()
                    size = remaining
                    while remaining:
                        block = stream.read(min(1024*1024, remaining))
                        if not block:
                            raise RuntimeError('Truncated baseline blob output')
                        h.update(block)
                        remaining -= len(block)
                    if stream.read(1) != b'\n':
                        raise RuntimeError('Missing cat-file record delimiter')
                    blobs[oid] = {'sha256': h.hexdigest(), 'bytes': size}
                if stream.read(1):
                    raise RuntimeError('Unexpected extra baseline cat-file bytes')
        for item in items:
            base_entry = item['baseline_tree_entry']
            if base_entry and base_entry['object_id'] in blobs:
                blob = blobs[base_entry['object_id']]
                item['baseline_blob_sha256'] = blob['sha256']
                item['baseline_blob_bytes'] = blob['bytes']
                item['baseline_identical_bytes'] = item['sha256'] == blob['sha256'] and item['bytes'] == blob['bytes']
        path = self.draft/'changes/binary-manifest.json'
        self.preserve_prior(path)
        dump(path, {'task_id': TASK, 'base_commit': BASE, 'generated_before_file_freeze_at_utc': utc(),
                    'count': len(items), 'items': items,
                    'scope': 'Included candidate binary files only. Same-source means identical raw bytes to same-path metadata.base_commit blob; not an attribution claim.',
                    'self_not_binary': 'This JSON does not list itself as binary; it is included as a normal frozen text file.'})
        self.result['binary_manifest'] = {'path': self.rel(path), 'sha256': digest(path)[0], 'count': len(items)}

    def clone_base(self, target: pathlib.Path) -> None:
        no_links(target, self.validation, allow_missing=True)
        assert_inside(target, self.validation)
        if target.exists():
            raise RuntimeError('Clone destination must not exist: '+str(target))
        self.git(['clone', '--no-hardlinks', '--no-checkout', '--local', '--no-tags', str(self.root), str(target)])
        attrs = target/'.git/info/attributes'
        no_links(attrs, self.validation, allow_missing=True)
        attrs.parent.mkdir(parents=True, exist_ok=True)
        attrs.write_text('* -text -filter -ident -working-tree-encoding\n', encoding='ascii')
        self.git(['checkout', '--detach', BASE], cwd=target)

    def walk_regular(self, target: pathlib.Path) -> dict[str, pathlib.Path]:
        assert_inside(target, self.validation)
        no_links(target, self.validation)
        files = {}
        for folder, dirs, names in os.walk(target, followlinks=False):
            parent = pathlib.Path(folder)
            if parent == target:
                dirs[:] = [d for d in dirs if d != '.git']
            for name in dirs:
                no_links(parent/name, self.validation)
            for name in names:
                path = parent/name
                if path == target/'.git':
                    continue
                no_links(path, self.validation)
                if not path.is_file():
                    raise RuntimeError('Non-regular clone file')
                files[path.relative_to(target).as_posix()] = path
        return files

    def populate_generator(self, target: pathlib.Path, entries: list[dict]) -> None:
        wanted = {e['path']: e for e in entries}
        for rel, path in self.walk_regular(target).items():
            if rel not in wanted:
                # Only individually checked files in this newly created validation clone.
                no_links(path, self.validation)
                assert_inside(path, target)
                path.unlink()
        # Remove only empty, individually checked clone directories so file/directory
        # replacements from the base are representable. Never recurse-delete a tree.
        for folder, dirs, names in os.walk(target, topdown=False, followlinks=False):
            path = pathlib.Path(folder)
            if path == target or '.git' in path.relative_to(target).parts:
                continue
            no_links(path, self.validation)
            assert_inside(path, target)
            if not any(path.iterdir()):
                path.rmdir()
        for rel, item in wanted.items():
            source, dest = self.root/rel, target/rel
            no_links(source, self.root)
            no_links(dest, self.validation, allow_missing=True)
            assert_inside(dest, target)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            h, size = digest(dest)
            if h != item['sha256'] or size != item['bytes']:
                raise RuntimeError('Generator copy differs from frozen bytes: '+rel)

    def compare(self, target: pathlib.Path, entries: list[dict]) -> dict:
        files = self.walk_regular(target)
        expected = {e['path']: e for e in entries}
        missing = sorted(set(expected)-set(files))
        extra = sorted(set(files)-set(expected))
        mismatches = []
        for rel in sorted(set(files) & set(expected)):
            h, size = digest(files[rel])
            if h != expected[rel]['sha256'] or size != expected[rel]['bytes']:
                mismatches.append({'path': rel, 'expected': expected[rel], 'actual_sha256': h, 'actual_bytes': size})
        return {'target': self.rel(target), 'expected_count': len(expected), 'actual_count': len(files),
                'missing': missing, 'extra': extra, 'mismatches': mismatches,
                'identical': not missing and not extra and not mismatches, 'checked_at_utc': utc()}

    def source_recheck(self, entries: list[dict]) -> dict:
        candidates, _ = self.inventory()
        wanted = {e['path']: e for e in entries}
        if set(candidates) != set(wanted):
            raise RuntimeError('Freeze candidate scope changed: '+json.dumps({'added': sorted(set(candidates)-set(wanted)), 'removed': sorted(set(wanted)-set(candidates))}))
        for item in entries:
            path = self.root/item['path']
            no_links(path, self.root)
            self.safe_db(path)
            h, size = digest(path)
            if (h, size) != (item['sha256'], item['bytes']) or path.stat().st_mtime_ns != item['mtime_ns_at_capture']:
                raise RuntimeError('Frozen original changed after capture: '+item['path'])
        return {'count': len(entries), 'all_originals_match_frozen_bytes': True, 'at_utc': utc()}

    def execute(self) -> dict:
        original_before = None
        try:
            self.phase = 'preconditions'
            no_links(self.root/'spec/metadata.json', self.root)
            metadata = json.loads((self.root/'spec/metadata.json').read_text(encoding='utf-8-sig'))
            if metadata.get('base_commit') != BASE:
                raise RuntimeError('Only the published local metadata.base_commit is allowed')
            original_before = self.original_state()
            self.result['original_repository_before'] = original_before
            self.result['formal_before'] = self.formal_check()
            self.git(['cat-file', '-e', BASE+'^{commit}'])
            self.phase = 'candidate-scope-and-binaries'
            candidates, _ = self.inventory()
            tree = self.base_tree()
            self.make_binary_manifest(candidates, tree)
            self.phase = 'freeze'
            candidates, excluded = self.inventory()
            init_excluded = [x for x in excluded if INIT_UUID in pathlib.PurePosixPath(x['path']).name and x['path'].endswith('.jsonl') and 'git-ignored-not-candidate' not in x['origins']]
            if len(init_excluded) != 2:
                raise RuntimeError('Expected exactly two filename-excluded initialization raw files, found '+str(len(init_excluded)))
            entries = self.hash_entries(candidates)
            project_manifest = self.draft/'changes/project-files.json'
            exclusions_manifest = self.draft/'changes/excluded-files.json'
            patch = self.draft/'changes/final.diff'
            for path in (project_manifest, exclusions_manifest, patch):
                self.preserve_prior(path)
            aggregate = hashlib.sha256(''.join(e['path']+'\0'+e['sha256']+'\n' for e in entries).encode('utf-8')).hexdigest()
            dump(project_manifest, {'schema_version': 1, 'task_id': TASK, 'base_commit': BASE,
                 'freeze_capture_finished_at_utc': utc(), 'run_id': self.run_id, 'count': len(entries),
                 'bytes': sum(x['bytes'] for x in entries), 'aggregate_sha256': aggregate,
                 'aggregate_format': 'sorted UTF-8 path + NUL + lowercase SHA256 + LF',
                 'candidate_definition': 'Current existing Git tracked files + normal untracked files + explicit AGENTS.md, minus the fully declared exclusions',
                 'scope_is_a_material_snapshot_not_team_freeze_time': True, 'files': entries})
            dump(exclusions_manifest, {'schema_version': 1, 'task_id': TASK, 'run_id': self.run_id,
                 'candidate_exclusions': excluded, 'excluded_list_count': len(excluded),
                 'filename_only_initialization_raw_count': len(init_excluded),
                 'explicit_derived_files': sorted(DERIVED_FILES), 'explicit_derived_prefixes': list(DERIVED_PREFIXES),
                 'live_instance_prefix': LIVE_PREFIX, 'cache_components': sorted(CACHE_PARTS),
                 'ignored_scope_note': 'Git-ignored directory prefixes are listed without reading/enumerating their contents; .git internal files are never project candidates.',
                 'preserved_scope_note': 'Other included task logs, screenshots, archived HAPs, SQLite main DBs paired with nonempty stopped WAL evidence, specs/tests/workflow/traces and materials are frozen without pass/fail filtering. WAL stability is checked by pre/post hashes and mtime; temporary audit copies alone are opened by SQLite.',
                 'binary_manifest_disposition': 'Generated before freeze and included as a normal text file; does not list itself as binary.',
                 'no_no-exceptions_claim': True})
            self.result['project_manifest'] = {'path': self.rel(project_manifest), 'sha256': digest(project_manifest)[0], 'count': len(entries), 'bytes': sum(x['bytes'] for x in entries), 'aggregate_sha256': aggregate}
            self.result['excluded_manifest'] = {'path': self.rel(exclusions_manifest), 'sha256': digest(exclusions_manifest)[0]}
            shutil.copyfile(project_manifest, self.run/'project-files.frozen.json')
            shutil.copyfile(exclusions_manifest, self.run/'excluded-files.frozen.json')
            self.phase = 'sqlite-disposable-copy-integrity'
            self.audit_databases(entries)
            self.phase = 'generator-clone'
            generator = self.run/'generator-project'
            self.clone_base(generator)
            self.populate_generator(generator, entries)
            self.result['generator_comparison'] = self.compare(generator, entries)
            if not self.result['generator_comparison']['identical']:
                raise RuntimeError('Generator working tree differs from frozen manifest')
            self.git(['add', '--all', '--force', '--', '.'], cwd=generator)
            self.phase = 'binary-diff'
            diff_stdout = self.git(['diff', '--cached', '--binary', '--full-index', '--no-ext-diff', '--no-textconv', BASE, '--'], cwd=generator)
            shutil.copyfile(diff_stdout, patch)
            self.result['patch'] = {'path': self.rel(patch), 'sha256': digest(patch)[0], 'bytes': patch.stat().st_size}
            # Keep a per-run exact patch even if a later retry replaces the canonical draft path.
            shutil.copyfile(patch, self.run/'final.diff')
            self.phase = 'reconstructed-clone-and-apply'
            reconstructed = self.run/'reconstructed-project'
            self.clone_base(reconstructed)
            self.git(['apply', '--check', '--binary', str(patch)], cwd=reconstructed)
            self.git(['apply', '--binary', str(patch)], cwd=reconstructed)
            self.phase = 'complete-byte-verification'
            comparison = self.compare(reconstructed, entries)
            self.result['reconstruction'] = comparison
            self.result['reconstructed_project'] = self.rel(reconstructed)
            if not comparison['identical']:
                raise RuntimeError('Reconstructed project differs from frozen manifest')
            self.result['source_after'] = self.source_recheck(entries)
            self.result['formal_after'] = self.formal_check()
            original_after = self.original_state()
            self.result['original_repository_after'] = original_after
            self.result['real_index_and_HEAD_unchanged'] = original_after == original_before
            if original_after != original_before:
                raise RuntimeError('Real index or HEAD changed during material verification')
            self.result['status'] = 'pass'
            self.result['statement'] = 'Declared frozen material scope reconstructed byte-for-byte from the published local base by the recorded binary patch. This is not application acceptance.'
        except BaseException as exc:
            self.result['status'] = 'failed'
            self.result['failed_phase'] = self.phase
            self.result['error'] = type(exc).__name__ + ': ' + str(exc)
            (self.run/'exception.txt').write_text(traceback.format_exc(), encoding='utf-8')
            if original_before is not None:
                try:
                    after = self.original_state()
                    self.result['original_repository_after_failure'] = after
                    self.result['real_index_and_HEAD_unchanged'] = after == original_before
                    self.result['formal_after_failure'] = self.formal_check()
                except BaseException as check_exc:
                    self.result['failure_postcheck_error'] = type(check_exc).__name__+': '+str(check_exc)
        finally:
            self.result['finished_at_utc'] = utc()
            dump(self.run/'result.json', self.result)
            # A new result pointer never destroys a prior run's original result/logs.
            dump(self.validation/'result.json', self.result)
        return self.result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', default='D:/HCUP/cml-spec28', help='This task root only (default: %(default)s)')
    p.add_argument('--execute', action='store_true', help='Freeze and verify; use only after Root explicitly sends GO. Without this flag no files are changed.')
    p.add_argument('--run-id', help='New safe validation run directory name; existing directories are rejected')
    p.add_argument('--formal-manifest', default='workflow/implementation/development-frozen-fingerprint-10.json')
    p.add_argument('--formal-hap', default='entry/build/default/outputs/default/entry-default-unsigned.hap')
    p.add_argument('--expected-hap-sha256', default='51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229')
    return p


def main() -> int:
    p = parser()
    args = p.parse_args()
    if not args.execute:
        p.print_help()
        return 0
    if pathlib.Path(args.root).resolve() != pathlib.Path('D:/HCUP/cml-spec28').resolve():
        p.error('Only D:/HCUP/cml-spec28 is authorized')
    if not re.fullmatch('[0-9a-f]{64}', args.expected_hap_sha256):
        p.error('expected HAP SHA256 must be 64 lowercase hexadecimal characters')
    result = Freeze(args).execute()
    print(json.dumps({k: result.get(k) for k in ('status', 'run_directory', 'project_manifest', 'patch', 'reconstructed_project', 'failed_phase', 'error')}, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
