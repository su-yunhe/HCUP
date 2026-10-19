"""场景二：隐私政策在应用内嵌页面打开并可返回（B1–B11、X3）。"""
from __future__ import annotations

from hypium import BY

from hypium_tests._common import ID_PRIVACY_ENTRY, ID_PRIVACY_WEB, PRIVACY_ENTRY, CloudMusicCase


class TestPrivacyPage(CloudMusicCase):

    def setUp(self) -> None:
        super().setUp()
        self.open_settings()

    def test_b1_to_b5_open_in_app(self):
        self.require_component(BY.key(ID_PRIVACY_ENTRY), "隐私政策入口缺少 id")
        self.driver.click(BY.text(PRIVACY_ENTRY))
        # B5：不等网页加载，3s 内标题与 Web 即可见
        self.assert_privacy_page("点击入口后 3s 内", timeout=3)
        self.require_component(BY.key(ID_PRIVACY_WEB), "Web 组件缺少 id")
        # B2：等待 3s 后仍未拉起外部浏览器
        self.driver.wait(3)
        self.assert_privacy_page("点击入口 3s 后")
        title_count = self.count(BY.text("隐私政策"))
        print(f"[info] 隐私页 BY.text('隐私政策') 计数 = {title_count}")
        self.assertGreaterEqual(title_count, 1)

    def test_b7_press_back_returns_settings(self):
        self.open_privacy()
        self.driver.press_back()
        self.assert_settings_page("隐私页系统返回一次后")

    def test_b7_press_back_while_loading(self):
        self.driver.click(BY.text(PRIVACY_ENTRY))
        self.require_component(BY.type("Web"), "隐私页未出现 Web", timeout=3)
        self.driver.press_back()  # 网页大概率仍在加载
        self.assert_settings_page("加载中返回后")

    def test_b8_title_back_button_returns_settings(self):
        self.open_privacy()
        # 隐私页唯一的按钮为标题栏左侧返回按钮
        buttons = self.buttons_by_position()
        self.assertGreaterEqual(len(buttons), 1, "隐私页标题栏缺少返回按钮")
        self.driver.click(buttons[0])
        self.assert_settings_page("点击标题栏返回按钮后")

    def test_b9_back_after_page_loaded(self):
        self.open_privacy()
        self.driver.wait(8)  # 给网页足够时间加载/重定向
        self.assert_privacy_page("等待网页加载后")
        self.driver.press_back()
        self.assert_settings_page("网页加载后系统返回一次")

    def test_b10_fast_double_click_single_page(self):
        entry = self.require_component(BY.text(PRIVACY_ENTRY), "缺少隐私政策入口")
        center = entry.getBoundsCenter()
        self.driver.click((center.x, center.y))
        self.driver.click((center.x, center.y))
        self.assert_privacy_page("快速连点入口后")
        self.driver.press_back()
        self.assert_settings_page("快速连点后返回一次")

    def test_b11_back_then_reenter(self):
        self.open_privacy()
        self.driver.press_back()
        self.assert_settings_page("第一次返回")
        self.open_privacy()
        self.driver.press_back()
        self.assert_settings_page("第二次返回")

    def test_b11_restart_then_reenter(self):
        self.open_privacy()
        CloudMusicCase.setUp(self)  # 冷启动回首页
        self.open_settings()
        self.open_privacy()
        self.driver.press_back()
        self.assert_settings_page("重启后重进隐私页再返回")

    def test_x3_full_flow_stays_in_app(self):
        self.open_privacy()
        self.driver.press_back()
        self.assert_settings_page("隐私页返回")
        self.driver.press_back()
        self.require_component(BY.type("TextInput"), "设置页返回后未回到首页", timeout=5)
        self.assert_home_hint("隐私页→设置→首页连续返回后")
        self.driver.start_listen_toast()
        self.driver.click(self.search_button())
        self.assertEqual(self.driver.get_latest_toast(timeout=3), "请输入搜索内容")
        self.assert_stay_home("全流程空搜索后")
