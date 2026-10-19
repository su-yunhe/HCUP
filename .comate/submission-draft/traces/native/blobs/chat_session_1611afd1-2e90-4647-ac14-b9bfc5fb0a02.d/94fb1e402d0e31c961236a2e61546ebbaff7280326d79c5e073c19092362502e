"""场景一：设置页显示 0.9.3 版本与完整入口（A1–A11、X2）。"""
from __future__ import annotations

import re

from hypium import BY, MatchPattern

from hypium_tests._common import BUNDLE, ID_VERSION, PRIVACY_ENTRY, VERSION_TEXT, CloudMusicCase


class TestSettingsVersion(CloudMusicCase):

    def test_a1_a2_bundle_version(self):
        dump = self.driver.shell(f"bm dump -n {BUNDLE}")
        names = re.findall(r'"versionName":\s*"([^"]*)"', dump)
        codes = [int(c) for c in re.findall(r'"versionCode":\s*(\d+)', dump)]
        self.assertIn("0.9.3", names, f"bm dump 未见 versionName 0.9.3：{names}")
        self.assertNotIn("0.9.2", names, "bm dump 仍有 versionName 0.9.2")
        self.assertIn(103, codes, f"bm dump 未见 versionCode 103：{codes}")

    def test_a3_to_a11_settings_content(self):
        self.open_settings()
        self.assert_foreground("设置页")
        self.assertEqual(self.count(BY.text("设置")), 1, "设置页标题“设置”应唯一")
        for label in ["当前版本", "隐私政策", "问题反馈", PRIVACY_ENTRY]:
            self.assertEqual(self.count(BY.text(label)), 1, f"设置页“{label}”应存在且唯一")

        version = self.require_component(BY.text(VERSION_TEXT), f"版本值不是“{VERSION_TEXT}”")
        self.assertEqual(version.getText(), VERSION_TEXT)
        self.assertEqual(self.require_component(BY.key(ID_VERSION), "版本值缺少 id").getText(), VERSION_TEXT)
        self.assertIsNone(self.driver.find_component(BY.text("0.9.2", MatchPattern.CONTAINS)), "仍显示 0.9.2")

        author = self.require_component(BY.text("云音汇 @Chenlvin", MatchPattern.CONTAINS), "底部缺少“云音汇 @Chenlvin”")
        project = self.require_component(BY.text("CloudMusic-HarmonyOSNext", MatchPattern.CONTAINS),
                                         "底部缺少 GitHub 项目名称")

        # A11：版本与来源信息不滚动即同屏可见
        w, h = self.driver.get_display_size()
        for name, comp in [("版本值", version), ("底部作者", author), ("底部项目", project)]:
            b = comp.getBounds()
            self.assertTrue(0 <= b.top < b.bottom <= h and 0 <= b.left < b.right <= w,
                            f"{name} 不在屏幕内：{b}")

    def test_menu_dismiss_stays_home(self):
        self.open_more_menu()
        self.driver.press_back()
        self.driver.wait(1)
        self.assertTrue(self.gone(BY.text("设置")), "关闭菜单后“设置”仍可见")
        self.assertIsNone(self.driver.find_component(BY.text("当前版本")), "关闭菜单后不应进入设置页")
        self.assert_stay_home("关闭更多菜单后")

    def test_back_then_reenter(self):
        self.open_settings()
        self.driver.press_back()
        self.require_component(BY.type("TextInput"), "设置页返回后未回到首页", timeout=5)
        self.open_settings()
        self.assert_settings_page("返回后重进设置页")

    def test_restart_then_reenter(self):
        self.open_settings()
        self.setUp()  # 再次冷启动
        self.open_settings()
        self.assert_settings_page("重启应用后重进设置页")

    def test_x2_other_interactions_unchanged(self):
        self.open_settings()
        self.driver.start_listen_toast()
        self.driver.click(BY.text("问题反馈"))
        self.assertEqual(self.driver.get_latest_toast(timeout=3), "已复制邮箱地址到剪贴板")
        self.driver.wait(2.5)

        self.driver.start_listen_toast()
        self.driver.click(BY.text("云音汇 @Chenlvin", MatchPattern.CONTAINS))
        self.assertEqual(self.driver.get_latest_toast(timeout=3), "已复制链接到剪贴板")
        self.driver.wait(2.5)

        # 设置页顶栏：左=返回，右=分享
        share = self.buttons_by_position()[1]
        self.driver.start_listen_toast()
        self.driver.click(share)
        self.assertEqual(self.driver.get_latest_toast(timeout=3), "该功能暂未开发完成")
        self.assert_settings_page("设置页其余交互后")
