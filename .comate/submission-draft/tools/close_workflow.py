"""Coordinator-only close checkpoint after actual material checks, before final refreeze."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    names = ['changes/validation.json', 'verification/independent-replay.json', 'verification/content-audit.json']
    reports = {name: read(OUT / name) for name in names}
    if any(d.get('result') != 'pass' for d in reports.values()):
        raise ValueError('Do not close: current actual material checks have not all passed')
    current = read(OUT / 'changes/project-files.json')
    if reports['changes/validation.json']['patch_sha256'] != current['patch_sha256'] or reports['verification/independent-replay.json']['patch_sha256_before'] != current['patch_sha256']:
        raise ValueError('Do not close: replay checks do not match current patch')
    facts = read(OUT / 'evidence-facts.json')
    history = OUT / 'changes/history/pre-close'
    history.mkdir(parents=True, exist_ok=True)
    saved = []
    for name in names:
        target = history / name.replace('/', '--')
        if target.exists(): raise ValueError('Refuse to overwrite actual pre-close report snapshot')
        shutil.copy2(OUT / name, target)
        saved.append({'path': '.comate/submission-draft/' + target.relative_to(OUT).as_posix(), 'sha256': sha(target), 'original_report_at_close': name})
    result = {'task_id': 'cml-spec17', 'stage': '2-submit', 'closed_at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'draft_complete_with_explicit_pending_fields', 'formal_submission_ready': False,
              'business_source_changed_in_material_stage': False, 'production_files': 844,
              'production_aggregate_sha256': facts['production_fingerprint']['aggregate_sha256'],
              'pre_close_validated_tree': current['git_tree_oid'], 'pre_close_validated_patch_sha256': current['patch_sha256'],
              'pre_close_checks': saved,
              'final_patch_validation': '.comate/submission-draft/changes/validation.json',
              'final_independent_validation': '.comate/submission-draft/verification/independent-replay.json',
              'final_material_validation': '.comate/submission-draft/verification/final-audit.json',
              'note': 'The pre-close checks really passed. This new checkpoint and final state are then refrozen and replayed; final report paths are authoritative for the delivered tree.',
              'native_sessions_at_snapshot': len(facts['native_sessions']), 'copied_logs': len(facts['copied_logs']),
              'draft': '.comate/submission-draft/README.md', 'missing_fields': '.comate/submission-draft/missing-fields.md',
              'auto_facts': '.comate/submission-draft/auto-filled-facts.md', 'no_external_submission': True,
              'next_action': 'Stage 2 draft is complete. User fields and stage-3 global freeze/package remain separate; re-export active material-thread suffix at stage 3.'}
    write(ROOT / 'workflow/submit-stage-result-01.json', result)
    subprocess.run(['python', 'D:/HarmonyDev/codex/skills/harmony-task-flow/scripts/workflow.py', 'event', '--root', str(ROOT), '--phase', 'acceptance', '--status', 'local_validation_complete',
        '--reason', 'Actual draft content and clean complete-project root/independent replay passed; preserve pending user fields and close this checkpoint before final metadata refreeze.',
        '--next-action', 'Read final 2-submit material validation in .comate/submission-draft; stage-3 team fields, official freeze and packaging are not performed.',
        '--evidence', 'workflow/submit-stage-result-01.json'], check=True)
    state = read(ROOT / 'workflow/state.json')
    state['submission_stage'] = {'stage': '2-submit', 'status': result['status'], 'result': 'workflow/submit-stage-result-01.json', 'formal_submission_ready': False,
                               'final_checks': [result['final_patch_validation'], result['final_independent_validation'], result['final_material_validation']],
                               'active_native_suffix_requires_stage3_export': True}
    state['last_trace_snapshot'] = '.comate/submission-draft/traces/export-manifest.json'
    state['native_snapshot_gaps'] = facts['gaps']
    state.setdefault('approved_artifacts', {})['submit_materials_v01'] = [
        {'path': name, 'sha256': sha(ROOT / name)} for name in (
            'workflow/requirements/submit-review-01.md', 'workflow/design/submit-plan-01.md',
            'workflow/implementation/submit-materials-01.md', 'workflow/verification/submit-results-01.md')]
    write(ROOT / 'workflow/state.json', state)
    print(json.dumps({'status': result['status'], 'pre_close_tree': current['git_tree_oid'], 'refreeze_required': True}, ensure_ascii=False))

if __name__ == '__main__': main()
