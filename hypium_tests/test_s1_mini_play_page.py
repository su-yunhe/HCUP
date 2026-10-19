"""场景一：迷你播放器 ↔ 播放页（封面进入、向下箭头收起、播放/暂停状态一致）。"""
from __future__ import annotations

from hypium import BY

from hypium_tests.helpers import PlayerTestCase


class TestS1MiniPlayerPlayPage(PlayerTestCase):

    def test_01_no_mini_player_before_playing(self):
        """冷启动、尚未播放时不显示迷你播放器。"""
        self.restart()
        self.driver.wait(2)
        self.assertFalse(self.exists("mini_player"), "未播放时不应显示迷你播放器")

    def test_02_cover_opens_play_page_and_down_arrow_returns(self):
        """点封面进入全屏播放页，播放页显示同一首；向下箭头收起后迷你播放器恢复显示。"""
        self.start_playing()
        b = self.require_component(BY.key("mini_player"), "无迷你播放器").getBounds()
        w, h = self.driver.get_display_size()
        self.assertGreaterEqual(b.bottom, h * 0.85, f"迷你播放器不在屏幕底部: {b}")
        self.assertTrue(self.exists("mini_player_cover"), "迷你播放器没有专辑封面")
        self.assertEqual(self.text_of("mini_player_artist"), self.song.artists)

        self.open_play_page("mini_player_cover")
        self.assertFalse(self.exists("mini_player"), "播放页显示期间迷你播放器不应可见")
        self.assertEqual(self.text_of("play_page_title"), self.song.name)
        self.assertEqual(self.text_of("play_page_artist"), self.song.artists)
        self.assertTrue(self.exists("play_page_cover"), "播放页没有封面")
        self.assertTrue(self.exists("play_page_down"), "播放页没有向下箭头")
        self.assertIsNotNone(self.driver.find_component(BY.description("向下箭头")),
                             "向下箭头按钮缺少无障碍描述")

        self.close_play_page()
        self.assertEqual(self.text_of("mini_player_title"), self.song.name)
        self.assertEqual(self.text_of("mini_player_artist"), self.song.artists)
        self.assertTrue(self.exists("mini_player_pause_btn"), "收起后迷你播放器应仍为播放中")

    def test_03_pause_resume_in_play_page_syncs_mini_player(self):
        """播放页暂停 → 收起后迷你播放器为暂停态且时间不走；播放页继续 → 收起后为播放中且时间递增。"""
        self.start_playing()
        self.open_play_page()
        self.driver.click(BY.key("play_page_pause_btn"))
        self.assertTrue(self.exists("play_page_play_btn", timeout=5), "播放页点暂停后未切换为播放按钮")
        self.close_play_page()
        self.assertTrue(self.exists("mini_player_play_btn", timeout=3), "暂停后收起，迷你播放器应为暂停态")
        self.assertFalse(self.exists("mini_player_pause_btn"))
        t1 = self.time_of("mini_player_time")
        self.driver.wait(3)
        self.assertEqual(self.time_of("mini_player_time"), t1, "暂停后迷你播放器时间不应变化")

        self.open_play_page()
        self.assertTrue(self.exists("play_page_play_btn"), "再进播放页应仍为暂停态")
        self.driver.click(BY.key("play_page_play_btn"))
        self.assertTrue(self.exists("play_page_pause_btn", timeout=5), "播放页点播放后未切换为暂停按钮")
        self.close_play_page()
        self.assertTrue(self.exists("mini_player_pause_btn", timeout=3), "继续播放后收起，迷你播放器应为播放中")
        t2 = self.time_of("mini_player_time")
        self.driver.wait(4)
        self.assertGreater(self.time_of("mini_player_time"), t2, "继续播放后迷你播放器时间应递增")

    def test_04_mini_player_button_toggles_without_opening_play_page(self):
        """迷你播放器自带播放/暂停按钮：只切换状态，不打开播放页；播放页看到的状态一致。"""
        self.start_playing()
        self.driver.click(BY.key("mini_player_pause_btn"))
        self.assertTrue(self.exists("mini_player_play_btn", timeout=5), "点迷你栏暂停后未切换为播放按钮")
        self.driver.wait(1)
        self.assertFalse(self.exists("play_page"), "点迷你栏按钮不应打开播放页")
        self.open_play_page("mini_player")
        self.assertTrue(self.exists("play_page_play_btn"), "播放页应显示暂停态")
        self.close_play_page()
        self.driver.click(BY.key("mini_player_play_btn"))
        self.assertTrue(self.exists("mini_player_pause_btn", timeout=5), "点迷你栏播放后未切换为暂停按钮")
        self.assertFalse(self.exists("play_page"), "点迷你栏按钮不应打开播放页")

    def test_05_system_back_closes_play_page(self):
        """播放页按系统返回键，效果同向下箭头：回到原页面并显示迷你播放器。"""
        self.start_playing()
        self.open_play_page()
        self.driver.press_back()
        self.assertTrue(self.gone("play_page", timeout=8), "返回键未关闭播放页")
        self.assertTrue(self.exists("mini_player", timeout=5), "返回后迷你播放器未显示")
        self.require_text('"晴天" 的搜索结果', "返回键应回到搜索结果页", timeout=5)

    def test_06_rapid_clicks_open_once_and_close_once(self):
        """连点封面只打开一个播放页；连点向下箭头只返回一层（回到搜索结果页，不退到首页）。"""
        self.start_playing()
        x, y = self.center("mini_player_cover")
        for _ in range(3):
            self.driver.click((x, y))
        self.assertTrue(self.exists("play_page", timeout=8), "连点封面未进入播放页")
        self.driver.wait(1.5)
        dx, dy = self.center("play_page_down")
        for _ in range(3):
            self.driver.click((dx, dy))
        self.assertTrue(self.gone("play_page", timeout=8), "连点向下箭头后播放页未关闭")
        self.driver.wait(1.5)
        self.assertFalse(self.exists("play_page"), "连点封面不应叠加多个播放页")
        self.require_text('"晴天" 的搜索结果', "连点向下箭头应只返回一层，停在搜索结果页", timeout=5)
        self.assertTrue(self.exists("mini_player"), "返回后迷你播放器未显示")
