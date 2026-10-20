"""Read-only material checks; output confined to this derived validation directory."""
from pathlib import Path
import ast, datetime, hashlib, json, re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DRAFT = ROOT / '.comate/submission-draft'
TEMPLATES = Path('D:/SWE-OpenHarmony/templates')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

result = read(DRAFT / 'validation/patch-01/result.json')
canonical = ROOT / result['reconstructed_project']
frozen_draft = canonical / '.comate/submission-draft'

# Independent source/copy hashes for all existing log snapshots and all sixteen native exports.
logs = read(frozen_draft / 'logs/manifest.json')['files']
assert len(logs) == 106
log_results = []
for row in logs:
    paths = [ROOT / row['source'], DRAFT / row['snapshot'], frozen_draft / row['snapshot']]
    assert all(sha(p) == row['sha256'] and p.stat().st_size == row['bytes'] for p in paths)
    log_results.append({'source':row['source'], 'snapshot':row['snapshot'], 'sha256':row['sha256'], 'all_three_match':True})
native = read(frozen_draft / 'traces/manifest.json')
assert len(native['sessions']) == 16
assert len({row['session_id'] for row in native['sessions']}) == 16
assert native['snapshot_only'] is True and native['includes_future_events'] is False
trace_results = []
for row in native['sessions']:
    assert row['session_id'] != '01a13fc4-2611-7761-a580-1283e0c70541'
    for key, hash_key in [('raw','sha256'), ('markdown','markdown_sha256')]:
        assert sha(ROOT / row[key]) == sha(canonical / row[key]) == row[hash_key]
    with (canonical / row['raw']).open('rb') as stream:
        meta = json.loads(stream.readline())
    assert meta['type'] == 'session_meta' and meta['payload']['id'] == row['session_id']
    assert Path(meta['payload']['cwd']).resolve() == ROOT
    trace_results.append({'session_id':row['session_id'], 'raw':row['raw'], 'raw_sha256':row['sha256'], 'markdown':row['markdown'], 'markdown_sha256':row['markdown_sha256'], 'native_meta_id_cwd_match':True})
save('logs-native-parity.json', {'logs':log_results, 'native':trace_results, 'external_original_native_sources_opened':False, 'scope':'Task-export copies and frozen canonical only; raw initialization bodies not opened'})

template_text = (TEMPLATES / 'trace-index.md').read_text(encoding='utf-8-sig')
trace_text = (frozen_draft / 'trace-index.md').read_text(encoding='utf-8')
fields = [line[2:].rstrip('：') for line in template_text.splitlines() if line.startswith('- ')]
assert len(fields) == 24
missing_fields = [field for field in fields if not any(line.startswith('- '+field+'：') for line in trace_text.splitlines())]
assert not missing_fields, missing_fields

input_paths = [ROOT / 'spec/submit-input.yaml', ROOT.parent / 'common/spec-harness/team.yaml']
input_sha = [sha(p) for p in input_paths]
assert input_sha == ['37037bcd09c82cae1c83b8e3cca224f0927ef3b05a9f3b537c2f4053d5ece471','2d426ad41bf48e9ee36a2b69b93e41fcec6c2d5c0cd1ccfe8e7be1264710da39']
pending_text = (frozen_draft / 'pending-fields.md').read_text(encoding='utf-8')
pending_rows = [line.split('|')[1] for line in pending_text.splitlines() if re.match(r'^\|(?:submit-input\.|team\.)',line)]
assert len(pending_rows) == 13 and all('【待补充】' in line for line in pending_text.splitlines() if re.match(r'^\|(?:submit-input\.|team\.)',line))
expected_pending = ['submit-input.human_edits','submit-input.known_issues','submit-input.extra_sources','submit-input.md_export_dir','team.version','team.contact','team.freeze_time','team.members[0].name','team.members[0].work','team.source_guard','team.submitted_tasks','team.attempted_not_submitted','team.zip_out']
assert all(any(row.startswith(field) for row in pending_rows) for field in expected_pending)

fragment = read(frozen_draft / 'submission.json.fragment')
official = read(TEMPLATES / 'submission.json')
official_row = next(row for row in official['tasks'] if row['task_id'] == 'cml-spec28')
assert set(fragment) == set(official_row) and fragment['status'] == 'not_completed'
for key in ['project_path','build_instructions','trace_index']:
    assert '\\' not in fragment[key] and not fragment[key].startswith('/') and '..' not in Path(fragment[key]).parts
assert fragment['project_path'] == 'tasks/cml-spec28/project'
assert fragment['build_instructions'] == 'tasks/cml-spec28/build.md'
assert fragment['trace_index'] == 'tasks/cml-spec28/trace-index.md'

docs = ['README.md','build.md','trace-index.md','sources.fragment.md','solution.fragment.md','pending-fields.md','facts-and-sources.md','changes/project-scope.md']
links = []
for name in docs:
    text = (frozen_draft / name).read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+)\)', text):
        if re.match(r'https?://',link):
            links.append({'document':name,'link':link,'type':'external reference, not fetched'})
            continue
        if link.startswith('project/'):
            target = canonical / link[len('project/'):]
        elif link.startswith('../../traces/cml-spec28/'):
            target = DRAFT / 'traces' / link[len('../../traces/cml-spec28/'):]
        else:
            target = DRAFT / link
        assert target.exists(), (name,link,target)
        links.append({'document':name,'link':link,'resolved_path':target.relative_to(ROOT).as_posix(),'exists':True})
build_text = (frozen_draft / 'build.md').read_text(encoding='utf-8')
assert not re.findall(r'(?:[A-Za-z]:[\\/]|/Users/|/home/|/Applications/)',build_text)

helper = frozen_draft / 'tools/run-formal-acceptance.py'
helper_text = helper.read_text(encoding='utf-8')
ast.parse(helper_text)
required = ['assert args.device == module.DEVICE','assert out.is_relative_to(project)','not out.exists()', 'countTestCases() == 6','module.EVIDENCE = out / "ui"','old_before == old_after','id(sys.modules["hypium_tests.test_address_workflow"]) == module_identity','2 if counts.get("skip", 0) else 0','7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f']
assert all(s in helper_text for s in required)
assert helper_text.index('assert args.device == module.DEVICE') < helper_text.index('installed = command(')

save('materials-fields-links.json', {
    'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'official_trace_fields':{'count':24,'missing':missing_fields,'labels':fields},
    'user_pending':{'count':13,'fields':expected_pending,'input_sha256':input_sha,'all_explicitly_pending':True},
    'submission_fragment':fragment,'status_candidate_only':True,'no_team_zip_or_submission_created':True,
    'links':links,'trace_index_links':sum(x['document']=='trace-index.md' for x in links),
    'build_private_absolute_paths':[],
    'helper_static_review':{'sha256':sha(helper),'AST_parse':'pass','device_guard_before_install':True,'original_test_six_sha_guard':True,'output_only_EVIDENCE_configuration':True,'old_evidence_fingerprints_preserved':True,'skip_exit2':True,'executed_in_this_audit':False,'new_machine_device_build_acceptance':'not_run'},
    'version_AUTH_prose_review':'08/15 + 09/6 + 10/10 main31; extra3 separate; formal10 1pass5AUTHskip; not_completed; no official score or one-do pass claim',
    'staged_frozen_prose':'Generation-before-validation wording intentionally retained; actual completion is in external derived validation reports',
    'post_review_five_material_sessions_export':'not_run yet; Root will export after this audit stops writing',
    'template_hashes':{p.name:sha(p) for p in [TEMPLATES/'submission-checklist.md',TEMPLATES/'trace-index.md',TEMPLATES/'submission.json']}
})
print(json.dumps({'logs':len(log_results),'native_sessions':len(trace_results),'official_fields':len(fields),'pending_user_fields':len(expected_pending),'mapped_markdown_links':len(links),'trace_index_links':sum(x['document']=='trace-index.md' for x in links),'helper':'static pass, not executed'},ensure_ascii=False))
