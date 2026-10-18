"""场景三：本地曲库空列表提示 + 右上角上传本机音频。"""
from __future__ import annotations

import os
import tempfile

from hypium import BY, MatchPattern

from hypium_tests.cmu_helpers import T12, CmuTestCase

UPLOAD_MENU = BY.key("__NavdestinationField__NavigationMenu__MenuItem2__")
DEVICE_DIR = "/storage/media/100/local/files/Docs/Download"
SONG_FILE = "测试歌手 - 测试歌曲.mp3"
# MPEG-1 Layer III 128kbps 44.1kHz 单帧（417 字节）的静音数据
MP3_FRAME = bytes([0xFF, 0xFB, 0x90, 0x64]) + bytes(413)


class TestS3LocalSongs(CmuTestCase):

    def open_local_page(self) -> None:
        self.click_text("我的")
        self.click_text("本地曲库")
        self.require_component(UPLOAD_MENU, "未进入本地曲库页（缺少右上角上传入口）")
        self.driver.wait(1.5)

    def count_text(self):
        return self.find_or_none(BY.text("共 ", MatchPattern.STARTS_WITH), 3)

    def push_song(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        with os.fdopen(fd, "wb") as f:
            f.write(MP3_FRAME * 40)
        try:
            self.driver.push_file(path, f"{DEVICE_DIR}/{SONG_FILE}")
        finally:
            os.remove(path)

    def delete_all_songs(self) -> None:
        """多选 → 全选 → 删除 → 确认（基线 UI）。"""
        count = self.count_text()
        if count is None:
            return
        y = count.getBoundsCenter().y
        row_images = [c for c in (self.driver.find_all_components(BY.type("Image")) or [])
                      if abs(c.getBoundsCenter().y - y) < 40]
        max(row_images, key=lambda c: c.getBounds().left).click()  # 多选开关
        self.driver.wait(0.8)
        self.require_component(BY.type("CheckboxGroup"), "未进入多选").click()
        self.driver.wait(0.8)
        row_images = [c for c in (self.driver.find_all_components(BY.type("Image")) or [])
                      if abs(c.getBoundsCenter().y - y) < 40]
        min(row_images, key=lambda c: c.getBounds().left).click()  # 删除
        self.click_text("删除", timeout=5)
        self.driver.wait(1.5)

    # C1/C2：空列表提示文案（单个 Text，真实换行）
    def test_01_empty_tip(self):
        self.restart()
        self.open_local_page()
        self.require_precondition(self.count_text() is None, "本地曲库非空，无法验证空列表提示")
        tip = self.require_text(T12, f"未找到空列表提示 {T12!r}", timeout=5)
        self.assertEqual(tip.getText(), T12)
        self.assertIsNotNone(self.find_or_none(BY.key("local_empty_tip"), 2))
        self.assertTrue(self.require_component(UPLOAD_MENU, "").isClickable())
        # 返回后重进仍显示
        self.driver.press_back()
        self.driver.wait(1)
        self.click_text("本地曲库")
        self.require_text(T12, "返回重进后空列表提示消失", timeout=5)

    # C3/C4：上传弹窗取消 → 列表不变
    def test_02_upload_cancel(self):
        self.require_component(UPLOAD_MENU, "缺少上传入口").click()
        self.require_text("上传文件", "未弹出上传说明弹窗", timeout=5)
        self.click_text("取消")
        self.assertTrue(self.wait_gone(BY.text("上传文件"), 5))
        self.require_text(T12, "取消后列表状态变化", timeout=3)

    # C4/C5/C6：选择本机音频 → 添加到列表；重启后仍在；删除后回到空提示
    def test_03_upload_and_persist(self):
        self.push_song()
        try:
            self.require_component(UPLOAD_MENU, "缺少上传入口").click()
            self.click_text("上传", timeout=5)
            self.click_text("浏览", timeout=15)
            self.click_text("我的手机", timeout=10)
            self.click_text("Download", timeout=10)
            self.driver.start_listen_toast()
            song = self.require_component(BY.text("测试歌手 - 测试歌曲", MatchPattern.STARTS_WITH),
                                          "选择器中未找到测试音频", timeout=10)
            song.click()
            self.assertEqual(self.driver.get_latest_toast(timeout=8), "上传 1 个文件")
            self.require_text("共 1 首歌曲", "上传后列表未更新", timeout=8)
            self.require_text("测试歌曲", "列表缺少歌名", timeout=3)
            self.assertFalse(self.exists(BY.text(T12)), "列表非空时不应显示空提示")

            self.restart()
            self.open_local_page()
            self.require_text("共 1 首歌曲", "重启后上传的歌曲丢失", timeout=8)

            self.delete_all_songs()
            self.require_text(T12, "删除全部后未回到空列表提示", timeout=8)
        finally:
            self.driver.shell(f"rm -f '{DEVICE_DIR}/{SONG_FILE}'")
