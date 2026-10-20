"""Run explicitly selected cases with the unmodified common reporting classes."""
import argparse
import unittest
from pathlib import Path

from harness import env_check
from harness.report import RecordingResult, RunReport
from harness.runner import _collect_case_names, _inject_device_sn

from hypium_tests.evidence import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("cases", nargs="+")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromNames(args.cases)
    names = _collect_case_names(suite)
    _inject_device_sn(suite, args.device)
    warnings = env_check.check(args.device).warnings
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    report = RunReport(project=str(ROOT), device_sn=args.device,
                       env_warnings=warnings, cases=result.to_cases(names))
    report.print_summary()
    Path(args.json).write_text(report.to_json(), encoding="utf-8")
    return 0 if result.wasSuccessful() and len(report.cases) == len(args.cases) and all(
        case.outcome == "pass" for case in report.cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
