"""Run named HarnessTestCase methods with the same common result model."""
import argparse
from pathlib import Path
import unittest

from harness import device, env_check
from harness.runner import _collect_case_names, _inject_device_sn
from harness.report import RecordingResult, RunReport

parser = argparse.ArgumentParser()
parser.add_argument('--project', required=True)
parser.add_argument('--device', required=True)
parser.add_argument('--json', required=True)
parser.add_argument('--tests', nargs='+', required=True)
args = parser.parse_args()
sn = device.select_device(args.device)
warnings = env_check.check(sn).warnings
suite = unittest.TestLoader().loadTestsFromNames([
    'hypium_tests.test_webdav_backup.WebDavBackupTest.' + name for name in args.tests])
_inject_device_sn(suite, sn)
names = _collect_case_names(suite)
result = unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
report = RunReport(project=args.project,device_sn=sn,env_warnings=warnings,cases=result.to_cases(names))
report.print_summary()
Path(args.json).write_text(report.to_json(),encoding='utf-8')
raise SystemExit(0 if report.failed == 0 else 1)
