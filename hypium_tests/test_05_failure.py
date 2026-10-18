"""A3/A11/A50：API 不可用时卡片仍显示，进入私人FM失败也不崩溃（FM 队列为空）。

会临时把应用内 API 地址改成不可用的端口，用例结束时改回 fm_helpers.API_URL。
"""
from __future__ import annotations

import time

from hypium import BY

from harness.app import click_text_path
from harness.driver import HarnessTestCase
from hypium_tests import fm_helpers as fm

BAD_API_URL = "http://10.0.2.2:3999"


class TestFMFailure(HarnessTestCase):

    def set_api_url(self, url: str):
        fm.launch(self.driver)
        self.driver.click(self.driver.find_all_components(BY.text("我的"))[-1])
        time.sleep(1.5)
        click_text_path(self.driver, ["应用设置", "API与Cookie设置"])
        time.sleep(1.5)
        field = self.driver.find_all_components(BY.type("TextInput"))[0]
        self.driver.input_text(field, url)
        time.sleep(0.5)
        self.assertEqual(self.driver.find_all_components(BY.type("TextInput"))[0].getText(), url)
        self.driver.click(self.driver.find_component(BY.text("设置")))
        time.sleep(2)

    def tearDown(self):
        self.set_api_url(fm.API_URL)
        fm.launch(self.driver)
        fm.exit_fm_if_needed(self.driver)

    def test_01_enter_fm_without_server(self):
        self.set_api_url(BAD_API_URL)
        fm.launch(self.driver)
        fm.exit_fm_if_needed(self.driver)
        # A3：API 不可用时卡片仍在
        self.assertEqual(fm.text_of(self.driver, "fm_card_title"), "私人FM")
        song = fm.bottom_song(self.driver)

        fm.click_key(self.driver, "fm_card")
        self.assertIsNotNone(fm.wait_key(self.driver, "fm_badge_bottom"), "请求失败后也应进入私人FM并显示标识")
        self.assertTrue(fm.wait_gone(self.driver, "fm_card_loading", 20), "请求失败后加载状态未释放")
        self.assertEqual(fm.bottom_song(self.driver), song, "请求失败时不应改变当前显示的歌曲")

        # 空 FM 队列也能打开播放页
        fm.open_player(self.driver)
        self.assertEqual(fm.text_of(self.driver, "fm_badge_player_text"), "私人FM")
        self.assertIsNotNone(self.driver.find_component(BY.text("不喜欢")))
        fm.click_key(self.driver, "fm_dislike_btn")  # 没有当前 FM 歌：点击无效、不崩溃
        time.sleep(1)
        fm.click_key(self.driver, "player_close_btn")
        fm.wait_gone(self.driver, "player_slider")

        # 再点卡片重试一次，仍然失败但不崩溃、可再次点击
        fm.click_key(self.driver, "fm_card")
        self.assertTrue(fm.wait_gone(self.driver, "fm_card_loading", 20))

        fm.open_queue_from_bottom(self.driver)
        self.assertEqual(fm.text_of(self.driver, "fm_queue_tip"), "正在播放私人FM")
        self.assertEqual(fm.queue_count(self.driver), 0)
        fm.click_key(self.driver, "fm_exit_btn")
        self.assertTrue(fm.wait_gone(self.driver, "fm_queue_tip"))
        fm.close_overlay(self.driver)
        self.assertIsNone(fm.find(self.driver, "fm_badge_bottom"))

        pid = self.driver.shell(f"pidof {fm.BUNDLE}").strip()
        self.assertTrue(pid, "应用进程不存在（可能崩溃）")
