"""Combine actual independent checks; never upgrades stale or failed inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
VERIFY = OUT / 'verification'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    evidence = load(VERIFY / 'evidence-audit-final.json')
    content = load(VERIFY / 'content-audit.json')
    replay = load(VERIFY / 'independent-replay.json')
    project = load(OUT / 'changes/project-files.json')
    current_project_mismatches = [x['path'] for x in project['files'] if not (ROOT / x['path']).is_file() or
        (ROOT / x['path']).stat().st_size != x['bytes'] or sha(ROOT / x['path']) != x['sha256']]
    stale = []
    if evidence['evidence_facts_sha256_after'] != sha(OUT / 'evidence-facts.json'):
        stale.append('evidence-facts changed after evidence audit')
    for name, digest in content['input_sha256_after'].items():
        if sha(OUT / name) != digest:
            stale.append('content input changed: ' + name)
    if sha(OUT / 'changes/project-files.json') != replay['manifest_sha256_before']:
        stale.append('replay manifest changed')
    if sha(OUT / 'changes/final.diff') != replay['patch_sha256_before']:
        stale.append('replay patch changed')
    if sha(VERIFY / 'audit_delivery.py') != content['script_sha256']:
        stale.append('content audit script changed')
    if sha(VERIFY / 'audit_materials.py') != evidence['script_sha256']:
        stale.append('evidence audit script changed')
    if sha(VERIFY / 'replay_independently.py') != replay['script_sha256']:
        stale.append('replay script changed')
    good = (evidence['evidence_checks_pass'] and not evidence['native']['registered_not_exported'] and
            content['result'] == 'pass' and replay['result'] == 'pass' and not stale and not current_project_mismatches)
    rows = [
        ('SUB-01', '844 production files unchanged; 1-do evidence retained; no business build/device rerun', 'evidence-audit-final.json:production_before/production_after/do_stage'),
        ('SUB-02', 'Official templates and approved requirements independently read within authorized scope', 'content-audit.json:trace_fields; workflow/verification/submit-results-01.md'),
        ('SUB-03', 'All ten empty user fields remain explicit placeholders', 'content-audit.json:missing_user_fields'),
        ('SUB-04', 'Automatic facts have native/file evidence; unavailable official baseline log disclosed', 'evidence-audit-final.json; content-audit.json:token_table'),
        ('SUB-05', 'Eight required material categories exist and are readable', 'content-audit.json:checks.required_materials'),
        ('SUB-06', 'Complete binary patch replays to the entire declared project, not just production code', 'independent-replay.json'),
        ('SUB-07', 'Independent task-branch clone, baseline checkout, check/apply and full file hash comparison all succeeded', 'independent-replay.json:commands/missing/extra/mismatches'),
        ('SUB-08', 'Every changed binary has path, size, SHA and independently verified baseline same-content claims', 'content-audit.json:binary_inventory/zero_byte_failure_screenshot'),
        ('SUB-09', 'Generated caches excluded in export; failure evidence retained; production tree not cleaned', 'content-audit.json:unexpected_noise_paths; changes/excluded-files.json'),
        ('SUB-10', 'Production build/install/start use variables and delivered files; controlled historical script migration limits disclosed', 'content-audit.json:checks.build_scope_and_portability_disclosed'),
        ('SUB-11', 'All 24 official trace-index fields filled with facts or explicit missing/not-applicable states', 'content-audit.json:trace_fields'),
        ('SUB-12', 'Sources and solution fragments retain bounded local results, adopted policies and all known unrun/blocked boundaries', 'content-audit.json:known_boundaries; solution.fragment.md; sources.fragment.md'),
        ('SUB-13', 'Single-task JSON parses and all three paths are legal package-relative paths', 'content-audit.json:fragment'),
        ('SUB-14', 'All 15 registered task sessions exported; full JSONL/Markdown equivalence and excluded overview verified', 'evidence-audit-final.json:native'),
        ('SUB-15', 'Native and independent filtered sidebar ID relationships verified; missing child sidebar rows not fabricated', 'evidence-audit-final.json:native.sessions'),
        ('SUB-16', 'Original compile and UI failures, retries, repair and regression retained', 'evidence-audit-final.json:raw_selftests; round-01-content-audit.json'),
        ('SUB-17', 'Four actual local/common taskbook hashes verified; absent spec/history disclosed', 'evidence-audit-final.json:harness; evidence-facts.json:harness'),
        ('SUB-18', '301 original logs and copies have equal size and SHA', 'evidence-audit-final.json:logs'),
        ('SUB-19', 'Unprovided human edit declarations remain placeholders, not a claim of no human edits', 'human-changes.md; missing-fields.md'),
        ('SUB-20', 'Complete-line snapshot boundaries, no native content rewrite, unavailable fields and source coordinates disclosed', 'evidence-audit-final.json:native; trace-index.md; missing-fields.md'),
        ('SUB-21', 'Project tree/manifest/patch are one verified frozen version; user official freeze time remains a placeholder', 'independent-replay.json; changes/project-files.json'),
        ('SUB-22', 'Explicit project/material boundary, complete package layout and package-relative Markdown references verified', 'content-audit.json:checks.package_layout_complete_and_safe/authored_markdown_links'),
        ('SUB-23', 'Separate user-missing and automatically filled fact lists provided', 'missing-fields.md; auto-filled-facts.md'),
        ('SUB-24', 'No official score, hidden-test or real payment claim; no upload, mail or team ZIP in this stage', 'solution.fragment.md; README.md')
    ]
    result = {'task_id': 'cml-spec17', 'stage': '2-submit', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'result': 'pass' if good else 'fail', 'scope': 'Independent local draft-material verification only; official acceptance, hidden tests and live authenticated transactions are not verified.',
        'script_sha256': sha(Path(__file__)), 'base_commit': project['base_commit'], 'git_tree_oid': project['git_tree_oid'],
        'project_file_count': project['file_count'], 'project_aggregate_sha256': project['aggregate_sha256'],
        'project_manifest_sha256': sha(OUT / 'changes/project-files.json'), 'patch_bytes': project['patch_bytes'],
        'patch_sha256': sha(OUT / 'changes/final.diff'), 'current_project_mismatches': current_project_mismatches,
        'stale_evidence': stale, 'production_aggregate_sha256': evidence['production_after']['actual_aggregate_sha256'],
        'native_sessions': evidence['native']['count'], 'copied_logs': evidence['logs']['count'],
        'binary_changes': content['binary_inventory']['declared_count'],
        'build_or_device_rerun': False, 'screenshot_needed_for_material_stage': False,
        'source_mappings': 'package-layout.json; evidence-facts paths are original draft-relative coordinates',
        'requirements': [{'id': sid, 'status': 'pass' if good else 'pending', 'finding': finding, 'evidence': evidence_ref}
                         for sid, finding, evidence_ref in rows],
        'evidence_reports': [{'path': 'verification/' + name, 'sha256': sha(VERIFY / name)} for name in (
            'evidence-audit-final.json', 'content-audit.json', 'independent-replay.json')],
        'prior_failure_retention': ['verification/round-01-content-audit.json', 'verification/round-01-content-audit.log',
            'verification/round-01-independent-replay.json', 'verification/round-01-independent-replay.log',
            'verification/metadata-scope-failure-01.json', 'verification/round-02-layout-failure-content-audit.json',
            'verification/round-02-layout-failure-content-audit.log'],
        'initial_material_failure': {'id': 'MAT-CACHE-01', 'affected_requirements': ['SUB-09'],
            'expected': 'Generated __pycache__/.pyc do not enter the selected project',
            'actual_round_01': ['test-harness/harness/__pycache__/__init__.cpython-312.pyc',
                'test-harness/harness/__pycache__/device.cpython-312.pyc', 'test-harness/harness/__pycache__/env_check.cpython-312.pyc'],
            'resolution': 'Explicit export-only exclusion, source originals retained, corrected project replayed' if good else 'pending final proof'},
        'derived_search_index_failure': {'id': 'MAT-SCOPE-02', 'affected_requirements': ['SUB-14', 'SUB-20'],
            'evidence': 'verification/metadata-scope-failure-01.json',
            'resolution': 'Unrelated hit UUID metadata replaced by counts in regenerated derived index; original task native bodies unchanged' if good else 'pending final proof',
            'final_unrelated_uuid_metadata_count': evidence['native'].get('unrelated_uuid_metadata_count')},
        'material_mapping_failure': {'id': 'MAT-LAYOUT-03', 'affected_requirements': ['SUB-22'],
            'evidence': 'verification/round-02-layout-failure-content-audit.json',
            'actual': 'A broad replay-* exclusion omitted 20 regular stdout/stderr command evidence files',
            'resolution': 'Exclude replay scratch directories and descendants only; retain regular command evidence files' if good else 'pending final proof'},
        'verification_test_correction': {'id': 'VERIFY-GROUP-01', 'classification': 'Invalid additional test assumption, not a production/material defect',
            'original_assumption': 'session_meta.session_id equals session_meta.id for every record',
            'observed': 'All 3 roots use their own grouping ID; all 12 children have session_meta.session_id equal to their actual parent_thread_id. session_meta.id is the actual child UUID.',
            'correction': 'Check the observed root/parent grouping relationship while retaining the original native UUID and independent sidebar assertions',
            'failed_assertion_evidence': 'verification/round-03-native-group-assumption-evidence-audit-final.json',
            'original_test': 'verification/round-03-native-group-assumption-audit_materials.py'},
        'remaining_information': ['User version/contact/freeze_time/member names/work/source_guard/human_edits/known_issues/extra_sources/md_export_dir remain unprovided',
            'Specified official baseline report path is absent; local preparation logs are separately provided',
            'Comate is not used; unexposed child sidebar IDs and unreported native fields are disclosed',
            'This technical snapshot excludes later messages and final responses; 3-package must refresh/freeze records'],
        'self_reference_policy': 'This report and the later material-files index are not hashed by this report itself. It hashes prior actual audit inputs and frozen project/patch. Material index is produced afterward.'}
    path = VERIFY / 'final-audit.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'result': result['result'], 'requirements': len(rows), 'stale_evidence': stale,
        'project_file_count': project['file_count'], 'current_project_mismatches': len(current_project_mismatches)}, ensure_ascii=False))
    if not good:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
