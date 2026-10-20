"""Two bounded cases, one device/UiDriver process, stable return + avatar rapid taps."""
import argparse
import os
from pathlib import Path
import unittest

from hypium import BY
from harness.report import RecordingResult, RunReport
from hypium_tests.test_login_acceptance import LoginAcceptance


class NavigationSmoke(LoginAcceptance):
    def test_three_returns_and_avatar_taps(self):
        """D4/E05/E06/E11: three stable reentries, including the actual avatar image."""
        for cycle in range(3):
            self.driver.press_back()
            self.driver.wait(1)
            entry = self._id("me_login_entry")
            point = entry
            if cycle == 2:
                row = entry.getBounds()
                images = []
                for component in self.driver.find_all_components(BY.type("Image")) or []:
                    box = component.getBounds()
                    if box.left >= row.left and box.right <= row.right and box.top >= row.top and box.bottom <= row.bottom and box.right > box.left:
                        images.append(component)
                self.assertTrue(images, "Actual avatar Image not found inside real login-entry row")
                point = min(images, key=lambda component: component.getBounds().left)
            box = point.getBounds()
            coordinate = ((box.left + box.right) // 2, (box.top + box.bottom) // 2)
            self.observed.setdefault("cycles", []).append({"cycle": cycle, "tap_point": coordinate, "avatar": cycle == 2})
            for _ in range(1 if cycle == 0 else 3):
                self.driver.click(coordinate)
            self._wait_stable_page("auth_login_page")
            self.driver.capture_screen(str(self.out / (self.case + "-cycle-" + str(cycle) + "-native.jpeg")))
            self._capture("-cycle-" + str(cycle))
            self._node("auth_login_page")
            self._node("auth_login_logo")
            self._nodes = None


parser = argparse.ArgumentParser()
parser.add_argument("--json", type=Path, required=True)
args = parser.parse_args()
NavigationSmoke.device_sn = os.environ["HDC_DEVICE"]
suite = unittest.TestSuite([NavigationSmoke("test_A01"), NavigationSmoke("test_three_returns_and_avatar_taps")])
names = [str(test) for test in suite]
result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult, failfast=True).run(suite)
report = RunReport(project=str(Path(__file__).resolve().parents[2]), device_sn=os.environ["HDC_DEVICE"], cases=result.to_cases(names))
args.json.write_text(report.to_json(), encoding="utf-8")
report.print_summary()
raise SystemExit(0 if result.wasSuccessful() else 1)
