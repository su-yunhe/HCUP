"""Run the affected nonempty-data cases with the unmodified common Harness reporter."""
import os
import unittest

from harness.env_check import check
from harness.report import RecordingResult, RunReport
from hypium_tests.test_restore_confirmation import RestoreConfirmationTests
from hypium_tests.verification_support import LOG, ROOT


def main():
    methods = ["test_05_prepare_nonempty_local_sentinel", "test_10_continuous_cancel_reopen_and_lifecycle",
               "test_11_nonempty_local_data_unchanged", "test_90_continue_positive_control"]
    RestoreConfirmationTests.device_sn = os.environ["HDC_DEVICE"]
    tests = [RestoreConfirmationTests(method) for method in methods]
    names = [str(test) for test in tests]
    environment = check(RestoreConfirmationTests.device_sn)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(unittest.TestSuite(tests))
    report = RunReport(project=str(ROOT), device_sn=RestoreConfirmationTests.device_sn,
                       env_warnings=environment.warnings, cases=result.to_cases(names))
    (LOG / "harness-report.json").write_text(report.to_json(), encoding="utf-8")
    report.print_summary()
    return 0 if report.failed == 0 and report.skipped == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
