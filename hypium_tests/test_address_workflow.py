"""Real-service UI tests. No token injection, fake service, or debug route.

Run only after installing the newly built cml-spec28 HAP on 11239.
Authentication absence is a skipped precondition, never a pass.
The lifecycle case creates and deletes only its own uniquely named address.
UI evidence alone does not prove add/update request counts; pair with NetLog.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

from hypium import BY
from harness.device import find_hdc
from harness.driver import HarnessTestCase


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "traces/development/verification/round2/ui"
BUNDLE = "com.joker.coolmall"
DEVICE = "127.0.0.1:11239"


def restart_app(driver, bundle):
    """Hypium cannot infer this bundle's main ability; use manifest EntryAbility."""
    driver.stop_app(bundle)
    driver.start_app(bundle, page_name="EntryAbility", wait_time=2)


class AddressWorkflowTests(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        if cls.device_sn != DEVICE:
            raise RuntimeError("cml-spec28 tests may operate only 127.0.0.1:11239")
        super().setUpClass()

    def setUp(self):
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        self.events = []
        self.started = time.time()
        restart_app(self.driver, BUNDLE)

    def tearDown(self):
        self.snapshot("final")
        (EVIDENCE / f"{self._testMethodName}-events.json").write_text(
            json.dumps({"device": DEVICE, "started": self.started,
                        "events": self.events}, ensure_ascii=False, indent=2),
            encoding="utf-8")

    def event(self, action, **values):
        self.events.append({"time": time.time(), "action": action, **values})

    def snapshot(self, phase):
        stem = f"{self._testMethodName}-{phase}"
        self.driver.capture_screen(str(EVIDENCE / f"{stem}.jpeg"))
        remote = f"/data/local/tmp/{stem}.json"
        for args in [("shell", "uitest", "dumpLayout", "-p", remote),
                     ("file", "recv", remote,
                      str((EVIDENCE / f"{stem}.json").relative_to(ROOT)))]:
            result = subprocess.run([find_hdc(), "-t", DEVICE, *args],
                                    cwd=ROOT, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=30)
            self.event("hdc", argv=list(args), exit_code=result.returncode,
                       stdout=result.stdout, stderr=result.stderr)

    @staticmethod
    def scroll_container_for(key):
        for prefix, container in [
            ("region_province_", "address_region_province_list"),
            ("region_city_", "address_region_city_list"),
            ("region_district_", "address_region_district_list"),
        ]:
            if key.startswith(prefix):
                return container
        if key in ["address_contact_input", "address_phone_input", "address_region_input",
                   "address_detail_input", "address_default_switch"]:
            return "address_form_scroll"
        if re.fullmatch(r"address_(row|contact|phone|region|detail|default|edit|delete)_[0-9]+", key):
            return "address_list"
        return None

    def in_view(self, target, container=None):
        bounds = target.getBounds()
        width, height = self.driver.get_display_size()
        left, top, right, bottom = 0, 0, width, height
        if container is not None:
            viewport = container.getBounds()
            left, top = max(left, viewport.left), max(top, viewport.top)
            right, bottom = min(right, viewport.right), min(bottom, viewport.bottom)
        return (bounds.right > bounds.left and bounds.bottom > bounds.top
                and bounds.left >= left and bounds.top >= top
                and bounds.right <= right and bounds.bottom <= bottom)

    def component(self, key, timeout=15):
        scroll_key = self.scroll_container_for(key)
        if scroll_key:
            container = self.require_component(BY.key(scroll_key), f"Missing scroll viewport: {scroll_key}", timeout)
            target = self.find_or_none(BY.key(key), timeout=.5)
            if target is None or not self.in_view(target, container):
                target = container.scrollSearch(BY.key(key), vertical=True, offset=20)
                self.event("scroll-search", container=scroll_key, key=key)
            self.assertIsNotNone(target, f"Cannot scroll {key} into {scroll_key}")
            self.assertTrue(self.in_view(target, container), f"{key} remains outside visible {scroll_key}")
            return target
        return self.require_component(BY.key(key), f"Missing stable component: {key}", timeout)

    def click(self, key):
        target = self.component(key)
        self.assertTrue(self.in_view(target), f"Cannot click off-screen component: {key}")
        self.driver.click(target)
        self.event("click", key=key)
        self.snapshot(f"step-{len(self.events):03d}-{key}")

    def text(self, key):
        value = self.component(key).getText()
        self.event("read", key=key, value=value)
        return value

    def enter(self, key, value):
        self.driver.input_text(self.component(key), value)
        self.assertEqual(self.text(key), value, f"Input did not retain {key}")
        self.event("input", key=key, value=value)

    def login_precondition(self):
        """Recognise observed chooser and real account/SMS forms.

        A lone word such as 登录 or 手机号 is insufficient: those may occur in
        unrelated pages. The chooser labels are exact observed UI strings.
        """
        for label in ["账号密码登录", "验证码登录", "账号登录", "短信登录"]:
            if self.find_or_none(BY.text(label), timeout=.5):
                return f"login chooser/title: {label}"
        has_submit = self.find_or_none(BY.text("登录"), timeout=.5)
        if not has_submit:
            return None
        has_phone = (self.find_or_none(BY.text("手机号"), timeout=.5)
                     or self.find_or_none(BY.text("手机号码"), timeout=.5))
        has_secret = (self.find_or_none(BY.text("密码"), timeout=.5)
                      or self.find_or_none(BY.text("验证码"), timeout=.5))
        if has_phone and has_secret:
            return "legal login form: phone + password/verification code + 登录"
        return None

    def require_order_or_auth(self):
        if self.find_or_none(BY.key("order_confirm_page"), timeout=3):
            return
        reason = self.login_precondition()
        if reason:
            self.event("auth-blocked", page=reason)
            self.snapshot("auth-blocked")
            self.skipTest(f"AUTH: natural order route opened {reason}; legal session required")
        self.component("order_confirm_page")

    def wait_list_or_auth(self):
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if self.find_or_none(BY.key("address_list_page"), timeout=.5):
                self.event("authenticated-list")
                return
            reason = self.login_precondition()
            if reason:
                self.event("auth-blocked", page=reason)
                self.snapshot("auth-blocked")
                self.skipTest(f"AUTH: natural entry opened {reason}; legal session required")
        self.fail("Neither address list nor known login screen appeared")

    def open_management(self):
        self.click("main_me_tab")
        self.click("me_address_entry")
        self.wait_list_or_auth()

    def open_selection(self):
        self.click("main_cart_tab")
        self.click("cart_confirm_order")
        self.require_order_or_auth()
        self.click("order_address_entry")
        self.wait_list_or_auth()

    def open_new(self):
        self.click("address_add_button")
        self.assertEqual(self.text("address_form_title"), "新增地址")
        self.component("address_form_ready")

    def select_region(self):
        self.click("address_region_input")
        self.component("address_region_picker")
        for key in ["region_province_440000", "region_city_440300", "region_district_440305"]:
            self.click(key)
        self.snapshot("region-selected")
        self.click("region_confirm")
        value = self.text("address_region_input")
        for text in ["广东省", "深圳市", "南山区"]:
            self.assertIn(text, value)

    def form_snapshot(self):
        return {key: self.text(f"address_{key}_input") for key in
                ["contact", "phone", "region", "detail"]} | {
                    "default": bool(self.component("address_default_switch").isChecked())}

    def test_00_cold_start_natural_unauthenticated_entries(self):
        """Entry diagnostic only: both real home paths reach legal login.

        A pass proves startup/navigation recovery, not A01/A02/C01 address
        behavior after authentication. This run has no legitimate account.
        """
        self.component("main_me_tab")
        self.component("main_cart_tab")
        self.click("main_me_tab")
        self.click("me_address_entry")
        reason = self.login_precondition()
        self.assertIsNotNone(reason, "Unauthenticated personal address entry did not reach legal login")
        self.event("natural-entry-diagnostic-pass", source="personal-center", login=reason)
        self.snapshot("personal-auth-reached")
        restart_app(self.driver, BUNDLE)
        self.click("main_cart_tab")
        self.click("cart_confirm_order")
        reason = self.login_precondition()
        self.assertIsNotNone(reason, "Unauthenticated cart confirmation entry did not reach legal login")
        self.event("natural-entry-diagnostic-pass", source="cart-confirm", login=reason)
        self.snapshot("cart-auth-reached")

    def test_01_new_form_and_empty_validation(self):
        """A01,A16,A17,B01-B06,B16,E01: visible controls and blank rejection."""
        self.open_management()
        self.assertEqual(self.text("address_add_button"), "新增地址")
        self.open_new()
        for label in ["联系人", "手机号", "所在地区", "详细地址", "设为默认地址"]:
            self.require_text(label, f"Spec label missing: {label}")
        for field in ["contact", "phone", "detail"]:
            self.assertEqual(self.text(f"address_{field}_input"), "")
        self.assertFalse(self.component("address_default_switch").isChecked())
        self.assertEqual(self.text("address_save_button"), "保存地址")
        self.click("address_save_button")
        self.component("address_form_error")
        self.component("address_form_ready")
        self.assertFalse(self.find_or_none(BY.key("address_list_page"), timeout=1))
        self.snapshot("blank-rejected")

    def test_02_region_confirm_cancel_and_draft(self):
        """B07-B11,E03,E05: complete region confirmation and cancel isolation."""
        self.open_management()
        self.open_new()
        before = self.text("address_region_input")
        self.click("address_region_input")
        self.click("region_province_440000")
        self.assertFalse(self.component("region_confirm").isEnabled(),
                         "Partial region must not be confirmable")
        self.click("region_cancel")
        self.assertEqual(self.text("address_region_input"), before)
        self.select_region()
        selected = self.text("address_region_input")
        self.click("address_region_input")
        self.click("region_province_430000")
        self.assertFalse(self.component("region_confirm").isEnabled(),
                         "Changing province must invalidate old city/district")
        self.click("region_cancel")
        self.assertEqual(self.text("address_region_input"), selected)

    def test_03_invalid_phone_preserves_draft(self):
        """B12-B14,B17-B18,E02: complete draft with explicitly invalid phone."""
        self.open_management()
        self.open_new()
        self.enter("address_contact_input", "独立验收草稿")
        self.enter("address_phone_input", "123")
        self.enter("address_detail_input", "独立验收街道1号")
        self.select_region()
        self.click("address_default_switch")
        self.assertTrue(self.component("address_default_switch").isChecked())
        self.click("address_default_switch")
        self.assertFalse(self.component("address_default_switch").isChecked())
        expected = self.form_snapshot()
        self.click("address_save_button")
        self.assertEqual(self.text("address_form_error"), "手机号格式不正确")
        self.assertEqual(self.form_snapshot(), expected)
        self.component("address_form_ready")
        self.snapshot("phone-rejected")

    def test_04_order_selection_cancel(self):
        """A02,C01,E22: real cart entry and cancelling selection preserves card."""
        self.click("main_cart_tab")
        self.click("cart_confirm_order")
        self.require_order_or_auth()
        before = {k: (c.getText() if (c := self.find_or_none(BY.key(k), timeout=1)) else None)
                  for k in ["order_address_contact", "order_address_phone",
                            "order_address_region", "order_address_detail"]}
        self.click("order_address_entry")
        self.wait_list_or_auth()
        self.driver.press_back()
        self.component("order_confirm_page")
        after = {k: (c.getText() if (c := self.find_or_none(BY.key(k), timeout=1)) else None)
                 for k in before}
        self.assertEqual(after, before)
        self.snapshot("selection-cancelled")

    def test_05_create_name_only_edit_reopen_select_delete(self):
        """Core real-service lifecycle; delete only id created by this exact test.

        Request count/method claims require paired NetLog analysis. Runs only when
        the coordinator permits normal authenticated address writes.
        """
        self.require_precondition(os.environ.get("CML28_ALLOW_ADDRESS_WRITES") == "1",
                                  "coordinator has not enabled own test-address lifecycle")
        self.open_management()
        self.open_new()
        contact = "验收" + uuid.uuid4().hex[:8]
        detail = "独立验收街道28号" + uuid.uuid4().hex[:4]
        self.enter("address_contact_input", contact)
        self.enter("address_phone_input", "13800138000")
        self.enter("address_detail_input", detail)
        self.select_region()
        self.assertFalse(self.component("address_default_switch").isChecked())
        original = self.form_snapshot()
        self.click("address_save_button")
        self.component("address_list_page", timeout=35)
        self.require_text(contact, "Newly saved contact absent from real list", timeout=25)
        self.snapshot("created")
        raw = json.loads((EVIDENCE / f"{self._testMethodName}-created.json").read_text(encoding="utf-8"))
        nodes = []
        def flatten(node):
            if isinstance(node, dict):
                if isinstance(node.get("attributes"), dict):
                    nodes.append(node["attributes"])
                for value in node.values():
                    flatten(value)
            elif isinstance(node, list):
                for value in node:
                    flatten(value)
        flatten(raw)
        matches = [n for n in nodes if n.get("text") == contact
                   and re.fullmatch(r"address_contact_.+", n.get("id", ""))]
        self.assertEqual(len(matches), 1, "Unique test address must have exactly one business id")
        address_id = matches[0]["id"].removeprefix("address_contact_")
        self.event("owned-test-address", id=address_id, contact=contact, detail=detail)
        for key, value in [("phone", original["phone"]), ("detail", detail)]:
            self.assertEqual(self.text(f"address_{key}_{address_id}"), value)
        self.click(f"address_edit_{address_id}")
        self.assertEqual(self.text("address_form_title"), "编辑地址")
        self.assertEqual(self.form_snapshot(), original)
        self.assertEqual(self.text("address_save_button"), "保存")
        renamed = contact + "改"
        self.enter("address_contact_input", renamed)
        expected = original | {"contact": renamed}
        self.assertEqual(self.form_snapshot(), expected)
        self.snapshot("name-only-before-save")
        self.click("address_save_button")
        self.component("address_list_page", timeout=35)
        self.assertEqual(self.text(f"address_contact_{address_id}"), renamed)
        self.assertFalse(self.find_or_none(BY.key("address_list_error"), timeout=1))
        self.click(f"address_edit_{address_id}")
        self.assertEqual(self.form_snapshot(), expected)
        self.snapshot("reopened")
        self.driver.press_back()
        self.component("address_list_page")
        self.click(f"address_delete_{address_id}")
        self.assertEqual(self.text("address_delete_message"), "确认删除该地址吗？")
        self.click("address_delete_cancel")
        self.component(f"address_row_{address_id}")
        # Re-enter via normal order path, select this exact row, and verify card.
        restart_app(self.driver, BUNDLE)
        self.open_selection()
        self.click(f"address_edit_{address_id}")
        self.assertEqual(self.text("address_form_title"), "编辑地址")
        self.assertFalse(self.find_or_none(BY.key("order_confirm_page"), timeout=1))
        self.driver.press_back()
        self.component("address_list_page")
        self.click(f"address_row_{address_id}")
        self.component("order_confirm_page")
        for key in ["contact", "phone", "detail"]:
            self.assertEqual(self.text(f"order_address_{key}"), expected[key])
        for value in ["广东省", "深圳市", "南山区"]:
            self.assertIn(value, self.text("order_address_region"))
        self.snapshot("selected-order-card")
        restart_app(self.driver, BUNDLE)
        self.open_management()
        self.assertEqual(self.text(f"address_contact_{address_id}"), renamed)
        self.click(f"address_delete_{address_id}")
        self.click("address_delete_confirm")
        self.component("address_list_page")
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and self.find_or_none(BY.key(f"address_row_{address_id}"), timeout=.5):
            self.driver.wait(.5)
        self.assertIsNone(self.find_or_none(BY.key(f"address_row_{address_id}"), timeout=1))
        self.snapshot("owned-test-address-deleted")
        restart_app(self.driver, BUNDLE)
        self.open_management()
        self.assertIsNone(self.find_or_none(BY.key(f"address_row_{address_id}"), timeout=1))
