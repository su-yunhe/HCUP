"""Explicit approved subset; omitted checks are recorded as not selected, never passes."""
import argparse
import json
import os
from pathlib import Path
import unittest
from harness.env_check import check
from harness.report import RecordingResult, RunReport
from hypium_tests.test_login_acceptance import LoginAcceptance

parser = argparse.ArgumentParser()
parser.add_argument("--selection", choices=["layout", "documents"], required=True)
parser.add_argument("--json", type=Path, required=True)
args = parser.parse_args()
layout = ["test_A03", "test_A04", "test_A05", "test_B03", "test_B05", "test_B06", "test_B07", "test_B08",
          "test_B12", "test_B13", "test_B14", "test_B15", "test_B17"]
layout += [f"test_C{i:02d}" for i in range(1, 8)]
layout += ["test_D5_runtime_rotation_layout", "test_E11_return_reenter_each_target"]
selected = layout if args.selection == "layout" else ["test_B14", "test_B15", "test_D4_documents_scroll_to_end_and_return"]
all_names = unittest.defaultTestLoader.getTestCaseNames(LoginAcceptance)
selection = {"kind": args.selection, "selected": selected, "not_selected": sorted(set(all_names) - set(selected)),
             "reason": "Phone full round covers unchanged ordinary content/actions; this round exercises real-window geometry/navigation, or fixes only the actual swipe API parameter."}
(args.json.parent / "selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
LoginAcceptance.device_sn = os.environ["HDC_DEVICE"]
suite = unittest.TestSuite(LoginAcceptance(name) for name in selected)
names = [str(test) for test in suite]
result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult, failfast=True).run(suite)
report = RunReport(project=str(Path(__file__).resolve().parents[2]), device_sn=os.environ["HDC_DEVICE"],
                   env_warnings=check(os.environ["HDC_DEVICE"]).warnings, cases=result.to_cases(names))
args.json.write_text(report.to_json(), encoding="utf-8")
report.print_summary()
raise SystemExit(0 if result.wasSuccessful() else 1)
