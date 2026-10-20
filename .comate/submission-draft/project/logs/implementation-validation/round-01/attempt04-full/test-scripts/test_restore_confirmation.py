"""Independent D1 cancellation tests. Run only after parent releases frozen source/device.

PowerShell must load the Harmony environment; PYTHONPATH must include the read-only
D:/HCUP/common/test-harness. Set VG_SPEC8_RELEASED=yes only after explicit release.
"""
from __future__ import annotations

import json
import os
import time

from harness.driver import HarnessTestCase
from hypium import BY

from hypium_tests.verification_support import (
    BUNDLE, CONFIG, LOG, PORT, MockDav, assert_release, hash_evidence, hdc,
    learning_snapshot, record, snapshot, source_fingerprint, write_json,
)


class RestoreConfirmationTests(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = assert_release()
        cls.device_sn = cls.device_sn or os.environ.get("HDC_DEVICE")
        if cls.device_sn != cls.manifest["device"]:
            raise RuntimeError("指定设备与本轮安装证据不一致")
        super().setUpClass()
        cls.driver.set_implicit_wait_time(.2)
        cls.mock = MockDav()
        cls.mock.start()
        try:
            cls.forward_before = hdc(cls.device_sn, "fport", "ls")
            if f"tcp:{PORT}" in cls.forward_before:
                raise RuntimeError(f"专用端口 {PORT} 已有转发，不能覆盖既有转发")
            hdc(cls.device_sn, "rport", f"tcp:{PORT}", f"tcp:{PORT}")
            cls.forward_added = True
        except Exception:
            cls.mock.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            if getattr(cls, "forward_added", False):
                hdc(cls.device_sn, "fport", "rm", f"tcp:{PORT}", f"tcp:{PORT}")
                hdc(cls.device_sn, "fport", "ls")
        finally:
            cls.mock.stop()
            write_json("source-fingerprint-after.json", source_fingerprint())
            hash_evidence()

    def setUp(self):
        assert_release()
        record("case_start", case=self.id())

    def tearDown(self):
        try:
            snapshot(self.device_sn, self._testMethodName + "-end")
            assert_release()
        finally:
            record("case_end", case=self.id())

    def component(self, key: str, timeout: float = 6, scroll: bool = False):
        if not scroll:
            return self.require_component(BY.key(key), f"稳定 id 不存在/不可定位: {key}", timeout=timeout)
        preferred = "UP" if key in ["webdav_restore_button", "webdav_save_button", "webdav_config_result", "webdav_restore_result"] else "DOWN"
        for attempt in range(12):
            component = self.driver.find_component(BY.key(key))
            direction = preferred
            if component is not None:
                bounds = component.getBounds()
                # Device's usable content is [380,2782]; keep all controls in the middle.
                # Clipped edge controls must be scrolled into view before clicking.
                if bounds.top >= 420 and bounds.bottom <= 2600:
                    return component
                direction = "UP" if bounds.bottom > 2600 else "DOWN"
            record("bounded_scroll_for_id", key=key, direction=direction, attempt=attempt)
            self.driver.swipe(direction, distance=35)
        self.fail(f"有界滚动后稳定 id 仍不可完整交互: {key}")

    def click_id(self, key: str, *, scroll: bool = False):
        component = self.component(key, scroll=scroll)
        record("click_id", key=key, text=component.getText(), enabled=component.isEnabled(), bounds=str(component.getBounds()))
        self.assertTrue(component.isEnabled(), f"控件不可用: {key}")
        self.driver.click(component)

    def absent(self, key: str, timeout: float = 6):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.driver.find_component(BY.key(key)) is None:
                return
            time.sleep(.1)
        self.fail(f"预期控件已关闭/消失: {key}")

    def navigate(self, restart: bool = False):
        if restart:
            record("stop_app", bundle=BUNDLE)
            self.driver.stop_app(BUNDLE)
            record("start_app", bundle=BUNDLE)
            self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=2)
        if self.find_or_none(BY.key("webdav_config_panel"), timeout=.4) is not None:
            return
        if self.find_or_none(BY.key("settings_section_sync"), timeout=.4) is None:
            self.click_id("nav_settings_entry")
        self.click_id("settings_section_sync", scroll=True)
        self.component("webdav_config_panel")
        restore = self.component("webdav_restore_button", scroll=True)
        self.assertEqual(restore.getText(), "从云端恢复", "A1 恢复入口原文")
        self.assertTrue(restore.isEnabled(), "A1 正常前置下入口可用")

    def configure(self, values: dict[str, str]):
        # Deliberately use only task-local sentinel credentials; never log prior values.
        for key, value in values.items():
            self.replace_field(key, value)
        toggle = self.component("webdav_autosync_toggle", scroll=True)
        nodes = snapshot(self.device_sn, "config-toggle-before")
        matches = [node for node in nodes if node.get("id") == "webdav_autosync_toggle"]
        self.assertEqual(len(matches), 1, "自动同步开关稳定 id 必须唯一")
        checked = matches[0].get("checked")
        self.assertIn(checked, ["true", "false", True, False], "自动同步状态必须可观察")
        if str(checked).lower() == "true":
            record("disable_autosync")
            self.driver.click(toggle)
        self.click_id("webdav_save_button", scroll=True)
        self.wait_saved()
        self.component("webdav_restore_button", scroll=True)
        time.sleep(1)
        nodes = snapshot(self.device_sn, "config-saved")
        self.assertTrue(any(node.get("id") == "webdav_autosync_toggle" and str(node.get("checked")).lower() == "false"
                            for node in nodes), "自动同步须关闭")
        record("configuration_ready", values=values, automatic_sync=False)

    def wait_saved(self):
        self.component("webdav_config_result", scroll=True)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            result = self.driver.find_component(BY.key("webdav_config_result"))
            if result is not None and result.getText() == "✅ WebDAV 设置已保存":
                record("configuration_saved", key="webdav_config_result", text=result.getText())
                return
            time.sleep(.2)
        self.fail("测试前置：webdav_config_result 未显示 ✅ WebDAV 设置已保存")

    def replace_field(self, key: str, value: str):
        component = self.component(key, scroll=True)
        known = getattr(type(self), "known_fields", {})
        text = component.getText()
        masked_known = key in ["webdav_password_input", "webdav_sync_password_input"] and known.get(key) == value and len(text) == len(value)
        if text == value or masked_known:
            record("config_already_known", key=key, value=value, masked=masked_known)
            return
        record("replace_config", key=key, value=value)
        self.driver.click(component)
        component.clearText()
        if value:
            self.driver.input_text(component, value)
        self.driver.press_back()
        known[key] = value
        type(self).known_fields = known

    def no_requests(self, baseline: int, stage: str):
        count = self.mock.checkpoint(stage, baseline, continueEverClicked=False)
        self.assertEqual(count["delta"], 0, f"{stage}: 未点击继续的累计窗口出现 WebDAV 请求: {count['requests']}")

    def open_dialog(self, stage: str, baseline: int):
        self.click_id("webdav_restore_button", scroll=True)
        self.component("webdav_restore_confirm_dialog")
        self.assertEqual(self.component("webdav_restore_confirm_cancel").getText(), "取消", "A3 D1 取消原文")
        self.assertEqual(self.component("webdav_restore_confirm_continue").getText(), "继续", "A15 D1 继续原文")
        self.assertIsNone(self.driver.find_component(BY.key("webdav_restore_request_loading")), "A17 确认阶段不得进入真实恢复 loading")
        nodes = snapshot(self.device_sn, stage + "-open")
        self.assertEqual(sum(node.get("id") == "webdav_restore_confirm_dialog" for node in nodes), 1,
                         "U6 D1 应保持单实例")
        self.no_requests(baseline, stage + "-open")

    def cancel_dialog(self, stage: str, baseline: int, system_back: bool = False):
        if system_back:
            record("system_back_close_d1")
            self.driver.press_back()
        else:
            self.click_id("webdav_restore_confirm_cancel")
        self.absent("webdav_restore_confirm_dialog")
        self.component("webdav_config_panel")
        restore = self.component("webdav_restore_button", scroll=True)
        self.assertEqual(restore.getText(), "从云端恢复", "A6 取消后入口原文")
        self.assertTrue(restore.isEnabled(), "A7 取消后入口可用")
        self.assertIsNone(self.driver.find_component(BY.key("webdav_restore_request_loading")), "A18 无残留恢复 loading")
        snapshot(self.device_sn, stage + "-cancel")
        self.no_requests(baseline, stage + "-cancel")

    def test_01_core_smoke(self):
        """Short tool/device smoke; same D1 assertions as the complete suite."""
        self.navigate(restart=True)
        self.configure(CONFIG)
        baseline = self.mock.count()
        self.open_dialog("smoke-first", baseline)
        self.cancel_dialog("smoke-first", baseline)
        self.open_dialog("smoke-reopen", baseline)
        self.cancel_dialog("smoke-reopen", baseline)

    def test_05_prepare_nonempty_local_sentinel(self):
        """Data setup via existing UI; DB copies are read-only and stay in this run's logs."""
        try:
            self.navigate(restart=True)
            self.configure(CONFIG)
            self.click_id("settings_header_back")
            self.click_id("settings_header_back")
            snapshot(self.device_sn, "sentinel-before-ui-seed")
            choose = self.find_or_none(BY.text("选择词书"), timeout=1)
            if choose is not None:
                record("sentinel_setup_click", text="选择词书")
                self.driver.click(choose)
            else:
                arrows = self.driver.find_all_components(BY.text("›")) or []
                self.assertEqual(len(arrows), 1, "哨兵数据前置：需可无歧义进入现有词书管理")
                record("sentinel_setup_click", text="›", validated_count=1)
                self.driver.click(arrows[0])
            plus = self.require_text("＋", "哨兵数据前置：现有创建词书入口")
            self.driver.click(plus)
            self.require_text("创建词书", "哨兵数据前置：现有创建弹层")
            fields = self.driver.find_all_components(BY.type("TextInput")) or []
            self.assertEqual(len(fields), 2, "哨兵创建弹层应有名称和标签两字段；不向未知输入注入")
            name = "VG8取消哨兵" + time.strftime("%H%M%S")
            record("seed_nonempty_book", name=name, method="existing create-book UI", deletes_existing=False)
            self.driver.input_text(fields[0], name)
            self.driver.press_back()
            self.driver.click(self.require_text("创建", "哨兵数据前置：创建按钮"))
            self.require_text(name, "哨兵创建须可读回")
            snapshot(self.device_sn, "sentinel-created")
            self.driver.stop_app(BUNDLE)
            data = learning_snapshot(self.device_sn, "sentinel-before")
            self.assertGreater(len(data.get("user_word_books", {}).get("rows", [])), 0,
                               "A16 需要非空哨兵，空数据不得冒充保护证据")
            type(self).sentinel_before = data
        except (AssertionError, RuntimeError, OSError) as error:
            write_json("sentinel-precondition-result.json", {"status": "blocked", "error": repr(error)})
            self.skipTest(f"A16非空哨兵前置阻断（核心取消用例继续）: {error}")
        finally:
            self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=2)
            self.navigate()

    def test_10_continuous_cancel_reopen_and_lifecycle(self):
        """A1-A15,A17-A19: continuous all-method zero window, no other network action."""
        self.navigate(restart=True)
        self.configure(CONFIG)
        # Re-entry reads persisted config/toggle; no counter reset is used afterwards.
        self.click_id("settings_header_back")
        self.navigate()
        self.component("webdav_autosync_toggle", scroll=True)
        nodes = snapshot(self.device_sn, "persisted-autosync-off")
        self.assertTrue(any(node.get("id") == "webdav_autosync_toggle" and str(node.get("checked")).lower() == "false"
                            for node in nodes), "关闭状态须持久化")
        baseline = self.mock.count()
        window_started = time.monotonic()
        record("continuous_zero_window_begin", baseline=baseline, continueEverClicked=False)
        for index in range(10):
            self.open_dialog(f"cycle-{index:02d}", baseline)
            time.sleep(.3)
            self.cancel_dialog(f"cycle-{index:02d}", baseline)
        # Derive coordinates from a freshly located stable target, only for repeat tempo.
        target = self.component("webdav_restore_button", scroll=True)
        bounds = target.getBounds()
        point = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        for index in range(4):
            record("rapid_restore_click", index=index, target="webdav_restore_button", point=point)
            self.driver.click(point)
        nodes = snapshot(self.device_sn, "rapid-restore-single-dialog")
        count = sum(node.get("id") == "webdav_restore_confirm_dialog" for node in nodes)
        self.assertLessEqual(count, 1, "快速动作不得叠加 D1")
        # A repeated hit on the restore point can land on the supported modal mask.
        # If the mask closed D1, reopen explicitly before repeated cancel attempts.
        if count == 0:
            self.open_dialog("rapid-followup", baseline)
        for index in range(3):
            cancel = self.driver.find_component(BY.key("webdav_restore_confirm_cancel"))
            if cancel is None:
                record("rapid_cancel_already_closed", index=index)
                break
            record("rapid_cancel_click", index=index, target="webdav_restore_confirm_cancel")
            self.driver.click(cancel)
        self.absent("webdav_restore_confirm_dialog")
        self.no_requests(baseline, "rapid-actions")
        for index in range(5):
            self.open_dialog(f"interleaved-{index:02d}", baseline)
            self.cancel_dialog(f"interleaved-{index:02d}", baseline)
        self.open_dialog("system-back", baseline)
        self.cancel_dialog("system-back", baseline, system_back=True)
        # In-page back and complete route back; do not use deep links.
        self.click_id("settings_header_back")
        self.navigate()
        self.open_dialog("section-reentry", baseline)
        self.cancel_dialog("section-reentry", baseline)
        self.click_id("settings_header_back")
        self.click_id("settings_header_back")
        self.navigate()
        self.open_dialog("route-reentry", baseline)
        self.cancel_dialog("route-reentry", baseline)
        self.navigate(restart=True)
        self.open_dialog("cold-restart", baseline)
        self.cancel_dialog("cold-restart", baseline)
        # Earlier actions/lifecycle transitions already belong to this same window.
        # Wait only the remainder needed to cross 125 s; progress is emitted every 15 s.
        while time.monotonic() - window_started < 125:
            time.sleep(min(15, 125 - (time.monotonic() - window_started)))
            self.no_requests(baseline, f"continuous-{int(time.monotonic() - window_started):03d}s")
        self.open_dialog("after-long-wait", baseline)
        self.cancel_dialog("after-long-wait", baseline)
        self.no_requests(baseline, "continuous-final")
        record("continuous_zero_window_end", baseline=baseline, count=self.mock.count(), continueEverClicked=False)

    def test_11_nonempty_local_data_unchanged(self):
        """A16: compare actual nonempty business entities after cancellation sequences."""
        before = getattr(type(self), "sentinel_before", None)
        self.require_precondition(before is not None, "A16 非空哨兵快照未准备成功")
        self.driver.stop_app(BUNDLE)
        try:
            after = learning_snapshot(self.device_sn, "sentinel-after-cancel")
            self.assertEqual(after, before, "A16 未授权打开/取消流程改变了本地学习/词书数据")
            write_json("sentinel-comparison.json", {"status": "pass", "entitiesEqual": True,
                       "nonemptyUserBooks": len(before["user_word_books"]["rows"]),
                       "before": "sentinel-before-entities.json", "after": "sentinel-after-cancel-entities.json"})
        finally:
            self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=2)
            self.navigate()

    def test_20_empty_and_whitespace_configuration(self):
        """U1 boundary; each field empty/whitespace, saved and unsaved, before D1 continue."""
        self.navigate()
        for saved in [False, True]:
            for value_name, value in [("empty", ""), ("spaces", "   ")]:
                for key in CONFIG:
                    self.configure(CONFIG)
                    record("boundary_field", key=key, value=value, saved=saved)
                    self.replace_field(key, value)
                    if saved:
                        self.click_id("webdav_save_button", scroll=True)
                        self.wait_saved()
                    stage = f"boundary-{key}-{value_name}-{'saved' if saved else 'draft'}"
                    baseline = self.mock.count()
                    self.open_dialog(stage, baseline)
                    self.cancel_dialog(stage, baseline)
        self.configure(CONFIG)

    def test_90_continue_positive_control(self):
        """Independent positive control, cloud empty: real HTTP only after explicit continue."""
        self.navigate()
        self.configure(CONFIG)
        self.mock.mode = "empty"
        baseline = self.mock.count()
        self.open_dialog("positive-control-before-continue", baseline)
        record("continue_authorization_boundary", baseline=baseline, key="webdav_restore_confirm_continue")
        self.click_id("webdav_restore_confirm_continue")
        self.absent("webdav_restore_confirm_dialog")
        deadline = time.monotonic() + 45
        while self.mock.count() == baseline and time.monotonic() < deadline:
            time.sleep(.1)
        self.assertGreater(self.mock.count(), baseline, "独立继续正控必须收到真实 WebDAV 请求，否则禁发零计数证据不充分")
        snapshot(self.device_sn, "positive-control-request-observed")
        restore = self.component("webdav_restore_button", timeout=45, scroll=True)
        deadline = time.monotonic() + 45
        while not restore.isEnabled() and time.monotonic() < deadline:
            time.sleep(.3)
            restore = self.component("webdav_restore_button")
        self.assertTrue(restore.isEnabled(), "继续后的既有无备份/失败流程须释放操作锁")
        self.component("webdav_restore_result", scroll=True)
        self.mock.checkpoint("positive-control-final", baseline, continueEverClicked=True)
        snapshot(self.device_sn, "positive-control-final")
        # A historical continue must not authorize the next invocation.
        next_baseline = self.mock.count()
        self.open_dialog("post-positive-new-dialog", next_baseline)
        self.cancel_dialog("post-positive-new-dialog", next_baseline)
