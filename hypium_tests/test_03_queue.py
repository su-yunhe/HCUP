"""场景二：播放列表面板中的“正在播放私人FM”与“退出FM”。"""
from __future__ import annotations

import time

from hypium import BY

from harness.driver import HarnessTestCase
from hypium_tests import fm_helpers as fm


class TestFMQueue(HarnessTestCase):

    def tearDown(self):
        for _ in range(2):
            if fm.find(self.driver, "queue_title") is None and fm.find(self.driver, "player_slider") is None:
                break
            self.driver.press_back()
            time.sleep(1)

    def test_01_exit_restores_manual_queue(self):
        """A10/A21/A22/A25-A29：面板提示与退出，退出后恢复手动队列并播放进入前的歌，面板保持打开。"""
        fm.launch(self.driver)
        fm.build_manual_queue(self.driver)
        fm.open_queue_from_bottom(self.driver)
        self.assertIsNone(fm.find(self.driver, "fm_queue_tip"), "普通模式不应显示“正在播放私人FM”")
        self.assertIsNone(fm.find(self.driver, "fm_exit_btn"))
        manual = fm.queue_names(self.driver)
        self.assertEqual(manual, [fm.SONG_A, fm.SONG_B])
        self.assertEqual(fm.queue_count(self.driver), 2)
        fm.close_overlay(self.driver)

        fm_song = fm.enter_fm(self.driver)
        fm.open_queue_from_bottom(self.driver)
        self.require_component(BY.text("正在播放私人FM"), "面板没有“正在播放私人FM”", timeout=5)
        exit_btn = self.require_component(BY.text("退出FM"), "面板没有“退出FM”按钮", timeout=5)
        self.assertTrue(fm.find(self.driver, "fm_exit_btn").isClickable())
        # FM 中面板列出的是推荐队列，隐藏清空按钮
        names = fm.queue_names(self.driver)
        self.assertIn(fm_song, names)
        self.assertIsNone(fm.find(self.driver, "queue_clean_btn"))

        mark = fm.mark(self.driver)
        self.driver.click(exit_btn)
        self.assertTrue(fm.wait_gone(self.driver, "fm_queue_tip"), "退出FM后提示未消失")
        self.assertIsNone(fm.find(self.driver, "fm_exit_btn"))
        # 面板保持打开，并立即刷新为手动队列
        self.assertIsNotNone(fm.find(self.driver, "queue_title"), "退出FM后面板不应关闭")
        self.assertTrue(fm.wait_for(lambda: fm.queue_count(self.driver) == 2, 5), "退出后数量不是手动队列的 2 首")
        self.assertEqual(fm.queue_names(self.driver), manual)
        self.assertIsNotNone(fm.find(self.driver, "queue_clean_btn"), "退出FM后清空按钮应恢复")
        fm.close_overlay(self.driver)
        self.assertIsNone(fm.find(self.driver, "fm_badge_bottom"), "退出FM后底部栏标识应消失")
        self.assertEqual(fm.bottom_song(self.driver), fm.SONG_A, "退出后应播放进入前的那首")
        self.assertEqual(fm.e1_ops_since(self.driver, mark), 0, "退出FM不应发推荐请求")
        self.assertEqual(fm.count_since(self.driver, mark, fm.LOG_E2), 0)

        # A31：再进出一轮，手动队列不被污染
        fm.enter_fm(self.driver)
        fm.exit_fm_if_needed(self.driver)
        fm.open_queue_from_bottom(self.driver)
        self.assertEqual(fm.queue_names(self.driver), manual)
        fm.close_overlay(self.driver)

    def test_02_exit_from_player_queue(self):
        """A23/A26/A18/A42：从播放页的播放列表按钮退出FM，播放页标识与不喜欢消失，循环按钮恢复。"""
        fm.ensure_fm_playing(self.driver)
        fm.open_player(self.driver)
        fm.click_key(self.driver, "player_queue_btn")
        self.assertIsNotNone(fm.wait_key(self.driver, "fm_queue_tip", 8), "播放页打开的面板没有私人FM提示")
        self.assertEqual(fm.text_of(self.driver, "fm_queue_tip"), "正在播放私人FM")
        fm.click_key(self.driver, "fm_exit_btn")
        self.assertTrue(fm.wait_gone(self.driver, "fm_queue_tip"))
        fm.close_overlay(self.driver)
        self.assertIsNotNone(fm.find(self.driver, "player_slider"), "应仍停留在播放页")
        self.assertTrue(fm.wait_gone(self.driver, "fm_badge_player"), "退出后播放页标识应消失")
        self.assertIsNone(self.driver.find_component(BY.text("不喜欢")))
        self.assertIsNotNone(fm.find(self.driver, "player_loop_btn"), "退出后循环模式按钮应恢复")

    def test_03_exit_with_empty_manual_queue(self):
        """A28 边界：进入前手动队列为空，退出后列表为空，底部栏显示“暂无播放”。"""
        fm.launch(self.driver)
        fm.exit_fm_if_needed(self.driver)
        fm.clear_queue(self.driver)
        fm.enter_fm(self.driver)
        fm.open_queue_from_bottom(self.driver)
        fm.click_key(self.driver, "fm_exit_btn")
        self.assertTrue(fm.wait_for(lambda: fm.queue_count(self.driver) == 0, 5), "退出后列表应为空")
        self.assertIsNotNone(fm.find(self.driver, "queue_title"))
        fm.close_overlay(self.driver)
        self.assertEqual(fm.bottom_song(self.driver), "暂无播放")
        self.assertIsNone(fm.find(self.driver, "fm_badge_bottom"))

    def test_04_other_entry_exits_fm(self):
        """A32/U10：FM 中从搜索单曲播放，自动退出私人FM。"""
        fm.ensure_fm_playing(self.driver)
        fm.search(self.driver, "外婆桥")
        fm.song_menu(self.driver, fm.SONG_B, "单曲播放")
        self.assertTrue(fm.wait_gone(self.driver, "fm_badge_bottom"), "其他入口播放后应退出私人FM")
        for _ in range(3):
            if self.driver.find_component(BY.text("搜索")) is None:
                break
            fm.close_overlay(self.driver)
        self.assertTrue(fm.wait_for(lambda: fm.bottom_song(self.driver) == fm.SONG_B, fm.NET_TIMEOUT))
