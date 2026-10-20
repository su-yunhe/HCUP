"""41 explicit requirements plus separately labelled recovery observations.

Run only after the coordinator freezes sources and installs this round's HAP.
Manual visual review and external OAuth are never converted to automatic passes.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import unittest

from hypium import BY
from harness.driver import HarnessTestCase

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow" / "verification"))
from cml_evidence import hdc_record, production_fingerprint, snapshot, write_json

PREFIX = "auth_login_"
PROVIDERS = ("wechat", "qq", "alipay")
LABELS = ("微信", "QQ", "支付宝")
FOOTER = "登录即代表同意《用户协议》和《隐私政策》"
REQUIREMENTS = [f"A{i}" for i in range(1, 16)] + [f"B{i}" for i in range(1, 20)] + [f"C{i}" for i in range(1, 8)]
VISUAL = {"A2", "A3", "A8", "A9", "A10", "A12", "A13", "B3", "B17", "B18", "B19"}
TARGETS = {
    "phone": ("auth_sms_login_page", "auth_account_login_page"),
    "account": ("auth_account_login_page", "auth_sms_login_page"),
    "user_agreement": ("common_user_agreement_page", "common_privacy_policy_page"),
    "privacy_policy": ("common_privacy_policy_page", "common_user_agreement_page"),
}


def flatten(node):
    yield node
    for child in node.get("children", []):
        yield from flatten(child)


def rect(attrs):
    values = [int(n) for n in re.findall(r"-?\d+", attrs["bounds"])]
    if len(values) != 4:
        raise AssertionError(f"Unrecognised raw bounds: {attrs['bounds']!r}")
    return values


def width(box):
    return box[2] - box[0]


def center(box):
    return (box[0] + box[2]) / 2


def text_of(node):
    own = node["attributes"].get("text", "")
    return own or "".join(text_of(child) for child in node.get("children", []))


class LoginAcceptance(HarnessTestCase):
    """No production changes, test hooks, fake credentials or breakpoint injection."""

    @classmethod
    def setUpClass(cls):
        run_dir = os.environ.get("CML_RUN_DIR")
        if not run_dir:
            raise unittest.SkipTest("Coordinator has not frozen/installed this round: CML_RUN_DIR absent")
        cls.out = Path(run_dir).resolve()
        cls.out.relative_to(ROOT / "logs")
        cls.install = json.loads((cls.out / "install-manifest.json").read_text(encoding="utf-8"))
        cls.frozen = json.loads((cls.out / "fingerprint-before.json").read_text(encoding="utf-8"))
        current = production_fingerprint()
        if current["sha256"] != cls.frozen["sha256"]:
            raise RuntimeError("Production inputs changed after freeze; evidence is invalid")
        if cls.install["source_sha256"] != current["sha256"]:
            raise RuntimeError("Installed artifact does not match this frozen source round")
        hap = Path(cls.install["hap_path"])
        hap.resolve().relative_to(ROOT)
        if hashlib.sha256(hap.read_bytes()).hexdigest() != cls.install["hap_sha256"]:
            raise RuntimeError("HAP differs from the freshly installed artifact")
        if cls.install["install_exit_code"] or "success" not in cls.install["install_output"].lower():
            raise RuntimeError("No successful fresh-HAP install evidence")
        cls.visual = {}
        review = os.environ.get("CML_VISUAL_REVIEW")
        if review:
            cls.visual = json.loads(Path(review).read_text(encoding="utf-8"))
            if cls.visual["source_sha256"] != current["sha256"] or cls.visual["hap_sha256"] != cls.install["hap_sha256"]:
                raise RuntimeError("Visual review belongs to another source or HAP")
        super().setUpClass()
        cls.driver.set_implicit_wait_time(0.2)
        cls.driver.stop_app("com.joker.coolmall")
        cls.driver.start_app("com.joker.coolmall", page_name="EntryAbility", wait_time=2)
        cls.rotation_before = cls.driver.get_display_rotation()
        if "CML_INITIAL_ROTATION" in os.environ:
            from hypium.model.basic_data_type import DisplayRotation
            cls.driver.set_display_rotation(DisplayRotation(int(os.environ["CML_INITIAL_ROTATION"])))
            cls.driver.wait(1)

    @classmethod
    def tearDownClass(cls):
        if "CML_INITIAL_ROTATION" in os.environ:
            cls.driver.set_display_rotation(cls.rotation_before)
            cls.driver.wait(0.5)
        after = production_fingerprint()
        write_json(cls.out / "fingerprint-after-hypium.json", after)
        if after["sha256"] != cls.frozen["sha256"]:
            raise RuntimeError("Source fingerprint changed during tests; invalidate affected evidence and rerun")

    def setUp(self):
        self.case = self._testMethodName
        self.observed = {"case": self.case, "time": time.time(), "requirements": getattr(self, self.case).__doc__}
        self._nodes = None
        self._enter_login()
        self._scroll_top()

    def tearDown(self):
        write_json(self.out / (self.case + ".observations.json"), self.observed)

    def _id(self, name, timeout=5):
        return self.require_component(BY.key(name), f"Missing visible real component: {name}", timeout=timeout)

    def _wait_stable_page(self, key, timeout=8):
        """Reject moving/clipped transition nodes; require 3 stable full-width samples."""
        deadline, previous, stable = time.monotonic() + timeout, None, 0
        samples = []
        while time.monotonic() < deadline:
            component = self.find_or_none(BY.key(key), timeout=0.1)
            if component:
                bounds = component.getBounds()
                box = [bounds.left, bounds.top, bounds.right, bounds.bottom]
                app_window = self.driver.get_current_window()
                window = app_window.getBounds()
                full_width = abs(box[0] - window.left) <= 1 and abs(box[2] - window.right) <= 1
                valid = width(box) > 0 and box[3] > box[1] and full_width and app_window.getBundleName() == "com.joker.coolmall"
                samples.append({"box": box, "window": [window.left, window.top, window.right, window.bottom], "full_width": full_width})
                stable = stable + 1 if valid and box == previous else 1 if valid else 0
                previous = box
                if stable >= 3:
                    self.observed.setdefault("stable_pages", {})[key] = samples
                    return component
            self.driver.wait(0.25)
        self.observed.setdefault("unstable_pages", {})[key] = samples
        self.fail(f"Page {key} did not settle at actual window width; transition/clip is not successful navigation")

    def _scroll_top(self):
        viewport = self._id("auth_login_scroll")
        for _ in range(4):
            logo = self.find_or_none(BY.key("auth_login_logo"), timeout=0.15)
            if logo:
                b, v = logo.getBounds(), viewport.getBounds()
                if b.bottom > b.top and b.top >= v.top and b.bottom <= v.bottom:
                    break
            self.driver.swipe("DOWN", distance=85, area=viewport)
            self.driver.wait(0.2)
        self._nodes = None

    def _scroll_footer(self):
        viewport = self._id("auth_login_scroll")
        scrolled = False
        for _ in range(6):
            footer = self.find_or_none(BY.key("auth_login_agreement_footer"), timeout=0.15)
            if footer:
                b, v = footer.getBounds(), viewport.getBounds()
                if b.bottom > b.top and b.top >= v.top and b.bottom <= v.bottom:
                    if scrolled:
                        self._capture("-after-footer-scroll")
                    self._nodes = None
                    return
            if not scrolled:
                self._capture("-before-footer-scroll")
            self.driver.swipe("UP", distance=85, area=viewport)
            self.driver.wait(0.2)
            scrolled = True
        self._capture("-footer-unreachable")
        self.fail("Footer cannot be reached by real scroll in current short-height viewport")

    def _enter_login(self, force_restart=False):
        if force_restart:
            self.driver.stop_app("com.joker.coolmall")
            self.driver.start_app("com.joker.coolmall", page_name="EntryAbility", wait_time=2)
        for _ in range(5):
            if self.find_or_none(BY.key("auth_login_page"), timeout=0.15):
                self._wait_stable_page("auth_login_page")
                return
            me = self.find_or_none(BY.key("main_tab_me"), timeout=0.15)
            if me:
                self.driver.click(me)
                self.driver.wait(0.3)
            entry = self.find_or_none(BY.key("me_login_entry"), timeout=0.15)
            if entry:
                self.driver.click(entry)
                self._wait_stable_page("auth_login_page")
                return
            self.driver.press_back()
            self.driver.wait(0.3)
        self.fail("Normal My -> login entry did not reach login main; preserve state and raw snapshots")

    def _capture(self, suffix=""):
        label = self.case + suffix
        snapshot(self.out, label)
        tree = json.loads((self.out / (label + ".ui.json")).read_text(encoding="utf-8"))
        self._nodes = list(flatten(tree))
        self.observed["snapshot"] = label
        return self._nodes

    def _node(self, key):
        if self._nodes is None:
            self._capture()
        found = [n for n in self._nodes if n["attributes"].get("key") == key or n["attributes"].get("id") == key]
        visible = [n for n in found if n["attributes"].get("visible", "true") != "false" and width(rect(n["attributes"])) > 0]
        self.assertEqual(len(visible), 1, f"Expected one visible {key}, got {len(visible)}")
        return visible[0]

    def _box(self, key):
        box = rect(self._node(key)["attributes"])
        self.observed.setdefault("bounds_px", {})[key] = box
        return box

    def _text(self, key, expected):
        node = self._node(key)
        self.assertEqual(text_of(node), expected)

    def _density(self):
        if self._nodes is None:
            self._capture()
        data = json.loads((self.out / (self.observed["snapshot"] + "-display.json")).read_text(encoding="utf-8"))["stdout"]
        matches = re.findall(r"^Density:\s*([0-9.]+)", data, re.M)
        self.assertTrue(matches, "No display density in raw metadata; cannot infer vp from pixels")
        density = float(matches[0])
        self.observed["density"] = density
        return density

    def _visual(self, req):
        if self._nodes is None:
            self._capture()
        item = self.visual.get("requirements", {}).get(req)
        if not item:
            self.skipTest(f"{req}: Screenshot collected; independent pixel/manual review is pending")
        self.assertTrue(item.get("evidence"), "Visual pass must name the reviewed pixels")
        evidence = item["evidence"]
        for name in ([evidence] if isinstance(evidence, str) else evidence):
            path = Path(name)
            if not path.is_absolute():
                path = ROOT / path
            path.resolve().relative_to(ROOT)
            self.assertTrue(path.is_file(), f"Reviewed screenshot absent: {path}")
        self.assertEqual(item["status"], "pass", item.get("notes", req))
        self.observed["visual_review"] = item

    def _icons(self):
        return [self._box(PREFIX + provider + "_icon") for provider in PROVIDERS]

    def _spacing(self):
        icons = sorted(self._icons())
        gaps = [icons[i + 1][0] - icons[i][2] for i in (0, 1)]
        self.observed["icon_gaps_px"] = gaps
        self.assertGreaterEqual(min(gaps), 0)
        self.assertLessEqual(abs(gaps[0] - gaps[1]), 1)

    def _layout(self, group):
        raw_page = self._box("auth_login_page")
        page = self._box("auth_login_content")
        region = self._box("auth_login_button_region")
        density = self._density()
        data = json.loads((self.out / (self.observed["snapshot"] + "-window.json")).read_text(encoding="utf-8"))["stdout"]
        self.observed["window_raw"] = data
        # U1 classifies the real window; U3 measures ratio/center against the
        # safe-area-inset content frame. These are intentionally distinct.
        match = re.search(r"^coolmall\d*\s+(?:-?\d+\s+){8}\[\s*(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s*\]", data, re.M)
        self.assertIsNotNone(match, "Cannot establish actual app-window width from hidumper")
        window = [int(v) for v in match.groups()]
        self.observed["window_xywh_px"] = window
        wvp = window[2] / density
        actual = "phone" if wvp < 600 else "tablet" if wvp < 840 else "large"
        self.observed.update({"width_vp": wvp, "actual_layout": actual})
        if group is not None and group != actual:
            self.skipTest(f"Real current page is {actual} ({wvp:.3f}vp); {group} window has not been exercised by this run")
        ratio = {"phone": 1.0, "tablet": 0.7, "large": 0.6}[actual]
        self.assertLessEqual(abs(width(region) - width(page) * ratio), 1, "Wrong measured region/page ratio")
        self.assertLessEqual(abs(center(region) - center(page)), 1, "Region not centered in actual page")
        return page, region

    def _navigate(self, action):
        if action in ("user_agreement", "privacy_policy"):
            self._scroll_footer()
        target, other = TARGETS[action]
        self.driver.click(self._id(PREFIX + action))
        self._wait_stable_page(target)
        self.assertIsNone(self.find_or_none(BY.key(other), timeout=0.2), "Wrong target is also visible")
        self._capture("-target")
        self._node(target)

    def _document(self, action):
        self._navigate(action)
        content_key = "common_" + action + "_content"
        self._id(content_key)
        node = self._node(content_key)
        actual = text_of(node)
        expected_path = ROOT / "workflow" / "verification" / "approved-document-fragments.json"
        if not expected_path.is_file():
            self.skipTest("Original approved document not handed off yet; navigation alone cannot prove real details")
        expected = json.loads(expected_path.read_text(encoding="utf-8"))[action]
        for fragment in expected["opening_fragments"]:
            self.assertIn(fragment, actual, "Substantive document fragment not readable in actual detail view")
        self.assertNotIn("页面内容视图", actual)
        self.observed["document_visible_text"] = actual

    def _check(self, req):
        if req in {f"B{i}" for i in range(12, 20)}:
            self._scroll_footer()
        if req == "A1":
            self.driver.press_back()
            self.driver.wait(1)
            self.driver.click(self._id("me_login_entry"))
            self._wait_stable_page("auth_login_page")
            self._capture()
            self._node("auth_login_page")
        elif req == "A2":
            self._id("auth_login_logo")
        elif req == "A3":
            self.assertLessEqual(self._box("auth_login_logo")[3], self._box("auth_login_button_region")[1])
        elif req == "A4":
            self._box("auth_login_page")
            self.assertLessEqual(abs(center(self._box("auth_login_logo")) - center(self._box("auth_login_content"))), 1)
        elif req == "A5":
            box = self._box("auth_login_logo")
            expected = 120 * self._density()
            self.assertLessEqual(abs(width(box) - expected), 1)
            self.assertLessEqual(abs(box[3] - box[1] - expected), 1)
        elif req in ("A6", "A10"):
            self._text(PREFIX + ("phone" if req == "A6" else "account"), "手机号登录" if req == "A6" else "账号密码登录")
        elif req in ("A7", "A11"):
            self.assertGreaterEqual(self._box(PREFIX + ("phone" if req == "A7" else "account"))[1], self._box("auth_login_logo")[3])
        elif req in ("A14", "A15"):
            self._navigate("phone" if req == "A14" else "account")
        elif req == "B1":
            self._text("auth_login_other_methods", "其他登录方式")
        elif req == "B2":
            self.assertGreaterEqual(self._box("auth_login_other_methods")[1], max(self._box(PREFIX + "phone")[3], self._box(PREFIX + "account")[3]))
        elif req == "B3":
            self.assertEqual(len(self._icons()), 3)
        elif req == "B4":
            for icon in self._icons():
                self.assertGreaterEqual(icon[1], self._box("auth_login_other_methods")[3])
        elif req == "B5":
            self._spacing()
        elif req in ("B6", "B7", "B8"):
            index = int(req[1:]) - 6
            icon, label = (PREFIX + PROVIDERS[index] + suffix for suffix in ("_icon", "_label"))
            self._text(label, LABELS[index])
            self.assertGreaterEqual(self._box(label)[1], self._box(icon)[3])
            self.assertLessEqual(abs(center(self._box(label)) - center(self._box(icon))), 1)
        elif req in ("B9", "B10", "B11"):
            self.skipTest(f"{req}: legal issued provider appId/signature/backend credentials and real authorization evidence are unavailable; not a pass")
        elif req in ("B12", "B13"):
            self._text(PREFIX + ("user_agreement" if req == "B12" else "privacy_policy"), "《用户协议》" if req == "B12" else "《隐私政策》")
        elif req in ("B14", "B15"):
            self._document("user_agreement" if req == "B14" else "privacy_policy")
        elif req == "B16":
            self._text("auth_login_agreement_footer", FOOTER)
        elif req == "B17":
            footer = self._box("auth_login_agreement_footer")
            # In a short scrolled window the preceding icons can be outside the
            # viewport. The last-content/bottom relationship is pixel-reviewed,
            # rather than incorrectly requiring every component on one screen.
            self.assertGreaterEqual(footer[1], self._box("auth_login_content")[1])
            self.assertLessEqual(footer[3], self._box("auth_login_content")[3])
        elif req in ("C1", "C2", "C3", "C4", "C5"):
            self._layout({"C1": "phone", "C2": "tablet", "C3": "tablet", "C4": "large", "C5": "large"}[req])
        elif req == "C6":
            self._layout(None)
            self._spacing()
        elif req == "C7":
            _, region = self._layout(None)
            for box in self._icons():
                self.assertGreaterEqual(box[0], region[0])
                self.assertGreaterEqual(box[1], region[1])
                self.assertLessEqual(box[2], region[2])
                self.assertLessEqual(box[3], region[3])
        elif req not in VISUAL:
            self.fail(f"Unimplemented requirement check: {req}")
        if req in VISUAL:
            self._visual(req)

    def test_E11_return_reenter_each_target(self):
        """D4 / E03 E09 E11: partial operation, system return, reenter; independent of 41 items."""
        for action in TARGETS:
            self.observed["current_action"] = action
            self._navigate(action)
            self.driver.press_back()
            self._wait_stable_page("auth_login_page")
            self.driver.click(self._id(PREFIX + action))
            self._wait_stable_page(TARGETS[action][0])
            self.driver.press_back()
            self._wait_stable_page("auth_login_page")
            self._nodes = None

    def test_E12_cold_restart_no_account(self):
        """D4 / E04 E07 E12: cold restart via normal entry without entering credentials."""
        self._enter_login(force_restart=True)
        self._capture()
        for key, text in [("phone", "手机号登录"), ("account", "账号密码登录"), ("other_methods", "其他登录方式")]:
            self._text(PREFIX + key, text)
        self._text("auth_login_agreement_footer", FOOTER)

    def test_E05_E06_rapid_repeat_navigation(self):
        """D4 / E05 E06: repeated same-entry and alternating taps, no unrecoverable page."""
        for actions in [("phone", "phone", "phone"), ("account", "account", "account"), ("phone", "account", "phone")]:
            positions = {}
            for action in ("phone", "account"):
                b = self._id(PREFIX + action).getBounds()
                positions[action] = ((b.left + b.right) // 2, (b.top + b.bottom) // 2)
            for action in actions:
                self.driver.click(positions[action])
            self.driver.wait(0.8)
            self._capture("-rapid-" + "-".join(actions))
            self.observed.setdefault("tap_sequences", []).append(actions)
            self.driver.press_back()
            self._wait_stable_page("auth_login_page")
            self._nodes = None

    def test_D3_missing_provider_configuration_recovery(self):
        """D3 / E03 E05 E06 E11: real unconfigured branch; never satisfies B9-B11."""
        expected_path = ROOT / "workflow/verification/provider-error-expectations.json"
        if not expected_path.is_file():
            self.skipTest("Provider error wording/node contract has not been handed off")
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        for provider in PROVIDERS:
            self.observed["current_provider"] = provider
            self._scroll_top()
            for _ in range(3):
                self.driver.click(self._id(PREFIX + provider + "_icon"))
            error = self._id("auth_login_error")
            self.assertEqual(error.getText(), expected[provider])
            self._capture("-missing-" + provider)
            self.assertIsNone(self.find_or_none(BY.key("auth_login_loading"), timeout=0.2), "No real request: must not leave fake/permanent HTTP loading")
            self.driver.click(self._id("auth_login_phone"))
            self._wait_stable_page("auth_sms_login_page")
            self.driver.press_back()
            self._wait_stable_page("auth_login_page")
            self._nodes = None

    def test_D4_documents_scroll_to_end_and_return(self):
        """U4 / E08 E11: original local text, real scrolling and readable end screenshots."""
        expected_path = ROOT / "workflow/verification/approved-document-fragments.json"
        if not expected_path.is_file():
            self.skipTest("Approved original document fragments not handed off")
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        for action in ("user_agreement", "privacy_policy"):
            self.observed["current_document"] = action
            self._document(action)
            before = self._box("common_" + action + "_content")
            for _ in range(8):
                self.driver.swipe("UP", distance=85, area=self._id(TARGETS[action][0]))
                self.driver.wait(0.2)
            self._capture("-" + action + "-end")
            after = self._box("common_" + action + "_content")
            self.observed.setdefault("document_scroll", {})[action] = {"before": before, "after": after}
            # UiTest may expose all Text even when clipped. End readability
            # therefore needs the real end screenshot in visual review.
            self.observed.setdefault("expected_document_end", {})[action] = expected[action]["ending_fragments"]
            self.driver.press_back()
            self._wait_stable_page("auth_login_page")
            self._nodes = None

    def test_D5_runtime_rotation_layout(self):
        """D5: rotate a real display and restore; classify by observed WMS dimensions."""
        if os.environ.get("CML_ALLOW_ROTATION") != "1":
            self.skipTest("This round was not assigned real display rotation")
        from hypium.model.basic_data_type import DisplayRotation
        original = self.driver.get_display_rotation()
        self.observed["original_rotation"] = str(original)
        try:
            self._layout(None)
            self._capture("-rotation-before")
            target = DisplayRotation.ROTATION_90 if original == DisplayRotation.ROTATION_0 else DisplayRotation.ROTATION_0
            self.driver.set_display_rotation(target)
            self.driver.wait(1)
            self._nodes = None
            self._scroll_top()
            self._layout(None)
            self._spacing()
            self._capture("-rotation-after")
            self._scroll_footer()
        finally:
            self.driver.set_display_rotation(original)
            self.driver.wait(1)
            self._nodes = None
            self._capture("-rotation-restored")

    def test_D6_title_avoids_status_bar_regression(self):
        """Observed v1.0 regression: the actual login title must avoid the system status-bar window."""
        self._capture()
        data = json.loads((self.out / (self.case + "-window.json")).read_text(encoding="utf-8"))["stdout"]
        match = re.search(r"^SCBStatusBar\d*\s+(?:-?\d+\s+){8}\[\s*(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s*\]", data, re.M)
        if not match or int(match.group(4)) == 0:
            self.skipTest("No measurable visible system status-bar window in this orientation")
        x, y, w, h = map(int, match.groups())
        title = self.require_text("登录", "Current login page title absent").getBounds()
        self.observed["status_bar_xywh_px"] = [x, y, w, h]
        self.observed["title_bounds_px"] = [title.left, title.top, title.right, title.bottom]
        self.assertGreaterEqual(title.top, y + h - 1, "Login title overlaps the system status bar (v1.0 regression)")


def make_requirement_test(req):
    def test(self):
        self._check(req)
    test.__doc__ = req + ": explicit acceptance item; see spec/acceptance.md"
    return test


for _req in REQUIREMENTS:
    setattr(LoginAcceptance, f"test_{_req[0]}{int(_req[1:]):02d}", make_requirement_test(_req))
