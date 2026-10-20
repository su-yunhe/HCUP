"""Observable vg-spec9 acceptance and separately labelled boundary regressions.

Run only after the main agent freezes source and grants the shared device lease.
Install the newly built task HAP immediately before each harness.runner invocation.
"""
from __future__ import annotations

import os
import re
import time
import unittest

from harness.driver import HarnessTestCase
from hypium import BY

from .evidence import OUTPUT, capture, event, hdc, save, source_fingerprint
from .webdav_fixture import WebDavFixture


def load_tests(loader, tests, pattern):
    """Optional explicit first-path run; omitted tests remain not_run in coverage."""
    selected = os.environ.get("VGSPEC9_TESTS", "")
    if not selected:
        return tests
    prefixes = tuple("test_" + item.strip() + "_" for item in selected.split(","))
    names = [name for name in loader.getTestCaseNames(WebDavLoadingTests) if name.startswith(prefixes)]
    if not names:
        raise RuntimeError("VGSPEC9_TESTS selected no test cases")
    return unittest.TestSuite(WebDavLoadingTests(name) for name in names)


class WebDavLoadingTests(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("VGSPEC9_SOURCE_FROZEN") != "1":
            raise RuntimeError("Main-agent source freeze and device lease are required (VGSPEC9_SOURCE_FROZEN=1)")
        cls.frozen = source_fingerprint()
        save("source-fingerprint-before.json", cls.frozen)
        cls.fixture = WebDavFixture(OUTPUT, int(os.environ.get("VGSPEC9_PORT", "18769")))
        cls.fixture.start()
        try:
            super().setUpClass()
            cls.driver.set_implicit_wait_time(0.3)
        except BaseException:
            cls.fixture.close()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.fixture.close()
        after = source_fingerprint()
        save("source-fingerprint-after.json", after)
        if after != cls.frozen:
            raise AssertionError("Production source changed: all affected runtime evidence is invalid")

    def setUp(self):
        self.assertEqual(self.frozen, source_fingerprint(), "Source changed during the frozen verification window")
        self.label = self._testMethodName
        self.scenario = None
        event("test_start", test=self.id())
        self.restart_and_enter()

    def tearDown(self):
        if self.scenario:
            self.scenario.release.set()
        capture(self.label + "-final", screenshot=True)
        self.assertEqual(self.frozen, source_fingerprint(), "Source changed; this test's evidence is invalid")
        event("test_end", test=self.id())

    def seek(self, key, direction="up", attempts=10):
        """Locate the stable UI key and scroll the existing configuration Scroll."""
        for _ in range(attempts):
            component = self.driver.find_component(BY.key(key))
            if component is not None:
                bounds = component.getBounds()
                if bounds.bottom > 300 and bounds.top < 2690:
                    return component
                direction = "down" if bounds.top < 300 else "up"
            self.driver.swipe(direction.upper(), distance=55)
            self.driver.wait(0.2)
        self.fail(f"Stable selector {key!r} was not visible on the existing UI")

    def restart_and_enter(self):
        hdc("shell", "aa", "force-stop", "io.qzz.weiyu")
        hdc("shell", "aa", "start", "-a", "EntryAbility", "-b", "io.qzz.weiyu")
        self.driver.wait(1)
        self.driver.click(self.require_text("⚙", "A1: existing homepage settings entry missing"))
        self.driver.click(self.require_text("WebDAV 配置", "A1: existing WebDAV settings entry missing"))
        self.require_component(BY.key("webdav_endpoint_input"), "A1: WebDAV configuration did not open")
        self.disable_auto_sync()

    def disable_auto_sync(self):
        toggle = self.seek("webdav_auto_sync_toggle")
        tree = capture(self.label + "-auto-sync")
        row = next((a for a in tree if a.get("id") == "webdav_auto_sync_toggle"), None)
        self.assertIsNotNone(row, "Fixture isolation requires an observable automatic-sync toggle")
        if row.get("checked") == "true":
            self.driver.click(toggle)
            tree = capture(self.label + "-auto-sync-disabled")
            row = next(a for a in tree if a.get("id") == "webdav_auto_sync_toggle")
        self.assertEqual("false", row.get("checked"), "Automatic sync must be off for manual request attribution")

    def fill(self, key, text):
        self.seek(key, direction="down")
        self.driver.input_text(BY.key(key), text)
        hdc("shell", "uitest", "uiInput", "keyEvent", "Back")

    def configure(self, mode="success", gate_first=True, delay=0.1, redirect_hops=0):
        root = (f"/vg-spec9-long-{time.time_ns()}/a/b/c/d/e/f" if mode == "long_tree" else None)
        self.scenario = self.fixture.create(self.label, root=root, mode=mode, gate_first=gate_first,
                                            delay=delay, redirect_hops=redirect_hops)
        for key, value in [
            ("webdav_endpoint_input", f"http://127.0.0.1:{self.fixture.port}"),
            ("webdav_username_input", self.fixture.USER),
            ("webdav_password_input", self.fixture.PASSWORD),
            ("webdav_sync_password_input", self.fixture.SYNC_PASSWORD),
            ("webdav_remote_root_input", self.scenario.root),
        ]:
            self.fill(key, value)
        self.seek("webdav_sync_now_button")
        self.assertEqual([], self.scenario.requests, "Editing must not be mistaken for the manual sync trigger")
        return self.scenario

    def sync_button(self):
        return self.seek("webdav_sync_now_button")

    def start_sync(self, rapid_clicks=1):
        button = self.sync_button()
        previous_count = len(self.scenario.requests)
        bounds = button.getBounds()
        point = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        event("sync_click_start", test=self.id(), root=self.scenario.root, clicks=rapid_clicks)
        for _ in range(rapid_clicks):
            self.driver.click(point)
        event("sync_click_return", test=self.id(), root=self.scenario.root)
        deadline = time.monotonic() + 15
        while len(self.scenario.requests) == previous_count and time.monotonic() < deadline:
            self.driver.wait(0.1)
        self.assertGreater(len(self.scenario.requests), previous_count, "A8/A9/A12/A13: clicked sync produced no new request at the configured endpoint")
        self.assertTrue(all(r["auth_matches_fixture"] for r in self.scenario.requests), "A2: request authentication differs from configured fixture")
        self.assertTrue(self.scenario.active, "Controlled in-progress request window ended before UI observation")
        return point

    def assert_loading(self, suffix):
        self.require_component(BY.key("webdav_sync_loading"), "A5/A7/A11: required loading indicator missing", timeout=3)
        self.require_type("LoadingProgress", "A5: actual ArkUI LoadingProgress type missing", timeout=3)
        tree = capture(self.label + "-" + suffix, screenshot=True)
        sample = event("ui_loading_sample", test=self.id(), root=self.scenario.root,
                       active_request_ids=list(self.scenario.active))
        rows = [a for a in tree if a.get("id") == "webdav_sync_loading"]
        self.assertEqual(1, len(rows), "A5: loading ID must identify one actual component")
        self.assertEqual("LoadingProgress", rows[0].get("type"), "A5: same-named ID is insufficient; actual component type differs")
        self.assertEqual("true", rows[0].get("visible"), "A5: LoadingProgress exists but is not visible")
        bounds = [int(n) for n in re.findall(r"-?\d+", rows[0].get("bounds", ""))]
        self.assertEqual(4, len(bounds), "LoadingProgress has no observable screen bounds")
        self.assertTrue(bounds[2] > bounds[0] and bounds[3] > bounds[1] and
                        bounds[0] < 1308 and bounds[2] > 0 and bounds[1] < 2880 and bounds[3] > 0,
                        "A5: LoadingProgress does not intersect the device viewport")
        self.assertTrue(any(r["epoch"] <= sample["epoch"] and
                            not any(p["request_id"] == r["request_id"] and p["epoch"] < sample["epoch"]
                                    for p in self.scenario.responses)
                            for r in self.scenario.requests), "A14: loader sample did not overlap a real in-progress request")

    def finish_sync(self, success=True, timeout=70):
        self.scenario.release.set()
        deadline = time.monotonic() + timeout
        sample_number = 0
        sampled_requests = set()
        result = ""
        while time.monotonic() < deadline:
            loader = self.driver.find_component(BY.key("webdav_sync_loading"))
            button = self.driver.find_component(BY.key("webdav_sync_now_button"))
            if self.scenario.active and loader is None:
                capture(self.label + "-early-loader-disappearance", screenshot=True)
                self.fail("A14: loading disappeared while a real backend request remained active")
            fresh_requests = set(self.scenario.active) - sampled_requests
            if fresh_requests and self.scenario.delay >= 3:
                self.assert_loading("phase-" + str(min(fresh_requests)))
                sampled_requests.update(fresh_requests)
            if button is not None and button.isEnabled():
                component = self.driver.find_component(BY.key("webdav_action_result"))
                result = component.getText() if component else ""
                if not self.scenario.active and result:
                    break
            sample_number += 1
            event("progress_sample", test=self.id(), active_request_ids=list(self.scenario.active),
                  loading_found=loader is not None, sample=sample_number)
            self.driver.wait(0.5)
        else:
            self.fail(f"A15/A16: synchronization did not reach an idle terminal state within {timeout}s")
        self.assertFalse(self.scenario.active, "Backend request still active at terminal UI")
        terminal_tree = capture(self.label + "-terminal-" + str(time.time_ns()))
        self.assertFalse(any(a.get("id") == "webdav_sync_loading" and a.get("visible") == "true"
                             for a in terminal_tree), "A15/A16: terminal UI still displays loading")
        if success:
            self.assertIn("同步完成", result, "Baseline successful sync chain did not complete (regression assertion, not a Spec-required message)")
        else:
            self.assertTrue("失败" in result or "错误" in result, "Fixture error did not reach the existing error result")
        event("sync_terminal", test=self.id(), root=self.scenario.root, success=success,
              result=result, requests=len(self.scenario.requests))
        return result

    def test_01_success_real_request_and_loading(self):
        """A1-A15: normal UI entry, valid fixture, actual request + typed visible loader."""
        self.configure(delay=5)
        self.start_sync()
        self.assert_loading("first-inflight")
        self.finish_sync()
        gets = [r for r in self.scenario.requests if r["method"] == "GET"]
        self.assertGreaterEqual(len(gets), 2, "Successful full chain must reach both existing download phases")

    def test_02_error_recovery_and_corrected_retry(self):
        """A16/B10: received HTTP403; finish, then correct fixture and retry successfully."""
        self.configure(mode="forbidden")
        self.start_sync()
        self.assert_loading("error-inflight")
        self.finish_sync(success=False)
        self.configure()
        self.start_sync()
        self.assert_loading("retry-inflight")
        self.finish_sync()

    def test_03_repeat_rapid_clicks_and_empty_remote(self):
        """A17/A18/B5-B7: empty remote, rapid initial clicks, busy clicks, next-round repeat."""
        self.configure()
        point = self.start_sync(rapid_clicks=3)
        self.assert_loading("rapid-inflight")
        for _ in range(3):
            self.driver.click(point)
        self.assert_loading("repeat-inflight")
        self.finish_sync()
        first_count = len(self.scenario.requests)
        self.scenario.gate_used = False
        self.scenario.release.clear()
        self.start_sync()
        self.assert_loading("second-round-inflight")
        self.finish_sync()
        self.assertGreater(len(self.scenario.requests), first_count, "Completed-round repeat did not issue fresh backend requests")

    def test_04_no_trigger_cancel_input_save_and_idle_reentry(self):
        """B3/B9/B11-B12: no sync click; edit/back, save, idle navigation and restart."""
        self.configure()
        self.driver.click(self.seek("webdav_save_button"))
        self.driver.wait(1)
        self.assertEqual([], self.scenario.requests, "Saving alone was incorrectly counted as manual sync")
        self.driver.click(self.require_text("←", "Existing settings header return missing"))
        self.driver.click(self.require_text("WebDAV 配置", "WebDAV entry missing after idle return"))
        self.seek("webdav_sync_now_button")
        self.assert_idle_loader("idle-return")
        self.restart_and_enter()
        self.seek("webdav_sync_now_button")
        self.assert_idle_loader("idle-restart")
        self.assertEqual([], self.scenario.requests, "No manual sync was triggered in the no-click scenario")

    def test_05_empty_and_whitespace_recovery(self):
        """B1/B2: regression only; invalid configurations must terminate without stale busy."""
        self.configure(gate_first=False)
        for key in ("webdav_endpoint_input", "webdav_username_input", "webdav_password_input", "webdav_sync_password_input"):
            for value in ("", "   "):
                original = {"webdav_endpoint_input": f"http://127.0.0.1:{self.fixture.port}",
                            "webdav_username_input": self.fixture.USER,
                            "webdav_password_input": self.fixture.PASSWORD,
                            "webdav_sync_password_input": self.fixture.SYNC_PASSWORD}[key]
                self.fill(key, value)
                self.driver.click(self.sync_button())
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    button = self.driver.find_component(BY.key("webdav_sync_now_button"))
                    if button is not None and button.isEnabled():
                        break
                    self.driver.wait(0.2)
                else:
                    self.fail(f"B1/B2: invalid {key} left UI busy")
                event("invalid_input_terminal", field=key, input_kind="empty" if not value else "whitespace")
                self.assert_idle_loader("invalid-" + key + ("-empty" if not value else "-space"))
                self.fill(key, original)
        self.assertEqual([], self.scenario.requests, "Invalid required configuration unexpectedly reached fixture")

    def test_06_long_chain_exceeds_old_wrapper_timeout(self):
        """A14/B13: real recursive parent-directory preparation exceeds120s; each reply8s."""
        self.configure(mode="long_tree", gate_first=False, delay=8)
        started = time.monotonic()
        self.start_sync()
        self.assert_loading("long-inflight-start")
        next_capture = started + 121
        while time.monotonic() < next_capture:
            self.assertIsNotNone(self.driver.find_component(BY.key("webdav_sync_loading")),
                                 "A14: loading stopped before long backend chain ended")
            self.driver.wait(1)
        self.assertTrue(self.scenario.active, "Long-chain fixture must still have a real request after120s")
        self.assert_loading("after-120s")
        self.finish_sync(timeout=420)
        elapsed = time.monotonic() - started
        self.assertGreater(elapsed, 120, "Long-chain test did not cross the former wrapper boundary")
        event("long_chain_complete", elapsed_seconds=elapsed)

    def test_07_inflight_return_reentry(self):
        """Approved U4 policy: the ongoing process-scoped operation rebinds on reentry."""
        self.configure(delay=8)
        self.start_sync()
        self.assert_loading("before-return")
        self.driver.click(self.require_text("←", "Existing settings header return missing"))
        self.driver.click(self.require_text("WebDAV 配置", "Reentry failed"))
        self.seek("webdav_sync_now_button")
        self.assertTrue(self.scenario.active, "Reentry did not occur during a real request; re-run with a longer multi-request window")
        self.assert_loading("after-reentry")
        self.finish_sync()

    def assert_idle_loader(self, suffix):
        tree = capture(self.label + "-" + suffix)
        self.assertFalse(any(a.get("id") == "webdav_sync_loading" and a.get("visible") == "true"
                             for a in tree), "Idle UI displays stale loading")

    def test_08_empty_directory_defaults_and_trimmed_config(self):
        """B1/B2 baseline compatibility: empty/space directory defaults, endpoint/user trim."""
        self.configure()
        for value in ("", "   "):
            self.scenario = self.fixture.create(self.label, root="/weiyu_sync")
            self.fill("webdav_remote_root_input", value)
            self.fill("webdav_endpoint_input", f"  http://127.0.0.1:{self.fixture.port}  ")
            self.fill("webdav_username_input", "  " + self.fixture.USER + "  ")
            self.start_sync()
            self.assert_loading("default-root-" + ("empty" if not value else "space"))
            self.finish_sync()

    def test_09_connection_failure_then_valid_retry(self):
        """B10: connection establishment failure recovers; successful retry is a new round."""
        self.configure(gate_first=False)
        self.fill("webdav_endpoint_input", "http://127.0.0.1:18771")
        self.driver.click(self.sync_button())
        self.finish_sync(success=False, timeout=80)
        self.assertEqual([], self.scenario.requests, "Unreachable endpoint must not count fixture requests as manual success")
        self.configure()
        self.start_sync()
        self.assert_loading("connection-retry")
        self.finish_sync()

    def test_10_inflight_edit_cannot_submit_other_operations(self):
        """Approved U6/B15: edits are next-round only; busy guards all submission entries."""
        self.configure(delay=8)
        self.start_sync()
        self.assert_loading("before-edit")
        self.fill("webdav_endpoint_input", "http://127.0.0.1:18771")
        self.fill("webdav_remote_root_input", "/vg-spec9-next-round-only")
        for key in ("webdav_save_button", "webdav_test_connection_button", "webdav_sync_now_button",
                    "webdav_backup_button", "webdav_restore_button"):
            self.assertFalse(self.seek(key).isEnabled(), f"Approved busy guard missing on {key}")
        self.seek("webdav_sync_now_button")
        self.assert_loading("after-edit")
        self.finish_sync()
        self.assertTrue(all(r["path"].split("?", 1)[0].startswith(self.scenario.root)
                            for r in self.scenario.requests), "Edited next-round root replaced the active round's request target")
