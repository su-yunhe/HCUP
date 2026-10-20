"""Audit final local evidence without rebuilding or operating a device."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads((ROOT / path).read_text('utf-8-sig'))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    checks = []

    def check(name, condition, details=None):
        checks.append({'check': name, 'pass': bool(condition), 'details': details})

    state = read('workflow/state.json')
    check('original_spec_unchanged', sha('spec/requirement.md') == state['spec_sha256'])
    check('original_metadata_unchanged', sha('spec/metadata.json') == state['metadata_sha256'])
    for group in ('analysis', 'functional_requirements', 'functional_design'):
        items = state['approved_artifacts'][group]
        check('approved_' + group, all(sha(x['path']) == x['sha256'] for x in items))
    check('frozen_manifest_matches_approved_hash',
          sha(state['code_fingerprint']['manifest']) == state['code_fingerprint']['manifest_sha256'])
    frozen = read(state['code_fingerprint']['manifest'])
    changed = [p for p, h in frozen['files_sha256'].items()
               if not (ROOT / p).is_file() or sha(p) != h]
    check('frozen_production_unchanged', not changed,
          {'files': len(frozen['files_sha256']), 'changed': changed})
    hap = read('traces/verification-do-r1/independent-hap-run-r2.json')
    check('current_hap_matches_independently_built_frozen_artifact',
          sha(hap['Path']) == hap['SHA256'] and Path(hap['Path']).stat().st_size == hap['Length'] and
          hap['FrozenManifest'] == state['code_fingerprint']['manifest'])
    run = ROOT / 'traces/verification-do-r1' / args.run_id
    context = json.loads((run / 'run-context.json').read_text('utf-8-sig'))
    check('actual_test_sources_match_run', all(
        sha('hypium_tests/' + p) == h for p, h in context['testSourceSHA256'].items()))
    tree = ast.parse((ROOT / 'hypium_tests/test_main_tabs.py').read_text('utf-8-sig'))
    expected = sorted(n.name for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name.startswith('test_'))
    cases = []
    observations = {}
    unchanged = []
    for name in expected:
        folder = run / name
        result_path = folder / 'case-result.json'
        result = json.loads(result_path.read_text('utf-8-sig')) if result_path.exists() else {}
        cases.append({'case': name, 'completed': result.get('completed', False)})
        difference = folder / 'source-difference.json'
        unchanged.append(difference.exists() and json.loads(difference.read_text('utf-8-sig')) == [])
        for record in result.get('observations', []):
            for item in record['items']:
                observations.setdefault(item, []).append(record['status'])
    check('all_discovered_cases_completed', len(expected) == 8 and all(x['completed'] for x in cases), cases)
    check('all_case_source_manifests_unchanged', all(unchanged))
    matrix = {f'A{i}': observations.get(f'A{i}', []) for i in range(1, 45)}
    check('A1_A44_all_observed_checks_pass', all(v and set(v) == {'pass'} for v in matrix.values()), matrix)
    command_file = 'logs/verification-do-run-' + args.run_id + '-commands.json'
    commands = read(command_file)
    runner = [c for c in commands if c['Label'] == 'runner']
    installs = [c for c in commands if c['Label'] == 'install-current-hap']
    check('runner_exit_zero_after_successful_fresh_install', len(runner) == 1 and
          runner[0]['ExitCode'] == 0 and len(installs) == 1 and installs[0]['ExitCode'] == 0 and
          installs[0]['Finished'] <= runner[0]['Started'])
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
              'run_id': args.run_id, 'production_aggregate': frozen['source_aggregate_sha256'],
              'checks': checks, 'passed': all(c['pass'] for c in checks),
              'scope': 'Local artifact audit; does not assert any official hidden-test score.'}
    output = ROOT / 'workflow/do-delivery-validation.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(json.dumps({'passed': report['passed'], 'checks': len(checks),
                      'failed': [c['check'] for c in checks if not c['pass']]}, ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
