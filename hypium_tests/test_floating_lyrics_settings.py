"""cmu-spec9「悬浮歌词设置选项扩展」本地自测用例。

依据 SWE-OpenHarmony/specs/cmu-spec9.md 的三个场景编写，不是官方评测用例。
通用能力（设备连接、重试、Slider 操作、窗口矩形）来自 SWE-OpenHarmony/test-harness。

运行：
    cd SWE-OpenHarmony
    PYTHONPATH=test-harness .venv/bin/python -m harness.runner \
        --project ../harmonycup-work/cmu-spec9

前置：应用在前台、位于底部 Tab“我的”页（或已停在“浮动歌词设置”页）。
用例会改动滑块，并在 finally 中恢复；失败也会恢复。
"""
from __future__ import annotations

from hypium import BY

from harness import window
from harness.app import click_text_path
from harness.driver import HarnessTestCase

# 自“我的”页出发。Spec 写作“播放设置”，基线 UI 上该入口实际文案为“播放与歌词”。
NAV_PATH = ["应用设置", "播放与歌词", "浮动歌词设置"]
FLOAT_WIN = "lyricsFloatWin"
# 滑块下标 = 页面自上而下的顺序
SIZE, WIDTH, OPACITY, POS_X, POS_Y = range(5)


class FloatLyricsCase(HarnessTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if len(cls.driver.find_all_components(BY.type("Slider")) or []) < 5:
            click_text_path(cls.driver, NAV_PATH)
            cls.driver.wait(1.5)

    def screen(self) -> tuple[int, int]:
        return self.driver.get_display_size()


class FloatingLyricsSettingsTest(FloatLyricsCase):
    """场景一：设置页控件齐全，滑块有即时反馈。"""

    def test_controls_present(self):  # TC-01
        for text in ("浮动歌词设置", "启用浮动歌词", "浮动歌词居中", "字体大小",
                     "宽度", "透明度", "左右调节", "上下调节", "背景模糊"):
            self.require_text(text, f"设置页应展示“{text}”。")
        self.assertEqual(len(self.sliders()), 5, "应有字体/宽度/透明度/左右/上下共 5 个滑块。")
        toggles = self.driver.find_all_components(BY.type("Toggle")) or []
        self.assertEqual(len(toggles), 3, "应有启用/居中/背景模糊共 3 个开关。")

    def test_font_size_slider_gives_immediate_feedback(self):  # TC-02
        original = self.slider_value(self.sliders()[SIZE])
        target = 25.0 if abs(original - 25.0) > 1 else 15.0
        try:
            actual = self.set_slider(SIZE, target, 10, 30)
            self.assertAlmostEqual(actual, target, delta=0.5, msg="字号滑块应能取到目标值。")
            self.assertEqual(self.text_after("字体大小"), f"{actual:.2f}",
                             "滑块右侧的数值文案应随滑块立即更新。")
        finally:
            self.set_slider(SIZE, original, 10, 30)


class FloatingLyricsPositionTest(FloatLyricsCase):
    """场景一步骤4 / 场景二：位置比例可调，且悬浮窗不应被调到屏幕外。"""

    def test_position_slider_offers_intermediate_values(self):  # TC-03
        original = self.slider_value(self.sliders()[POS_X])
        try:
            actual = self.set_slider(POS_X, 0.5, 0, 1)
            self.assertTrue(0.05 < actual < 0.95,
                            f"“左右调节”应能取到 0~1 之间的值，实际只得到 {actual}。")
        finally:
            self.set_slider(POS_X, original, 0, 1)

    def test_window_stays_visible_at_position_extremes(self):  # TC-10
        self.require_precondition(
            window.find_window_rect(self.driver.device_sn, FLOAT_WIN) is not None,
            f"悬浮窗 {FLOAT_WIN} 尚未创建（需联网播放后双击底栏封面）。")
        sw, sh = self.screen()
        sn = self.driver.device_sn
        originals = {i: self.slider_value(self.sliders()[i]) for i in (POS_X, POS_Y)}
        try:
            for idx, name in ((POS_X, "左右调节"), (POS_Y, "上下调节")):
                self.set_slider(idx, 1.0, 0, 1)
                rect = window.find_window_rect(sn, FLOAT_WIN)
                self.assertGreater(rect.visible_fraction(sw, sh), 0,
                                   f"“{name}”拖到最大后悬浮窗完全在屏幕外：{rect}，屏幕 {sw}x{sh}。")
                self.set_slider(idx, originals[idx], 0, 1)
        finally:
            for idx, v in originals.items():
                self.set_slider(idx, v, 0, 1)


class FloatingLyricsNotYetAutomated(FloatLyricsCase):
    """尚无法可靠自动化的场景，保持 skip，不得被读成通过。"""

    def test_position_restored_after_restart(self):  # TC-05
        self.skipTest("需要重启应用并双击底栏封面创建悬浮窗，且依赖联网播放中的歌曲；"
                      "改变窗口/播放状态，待确认后实现。窗口名 lyricsFloatWin，坐标读取用 harness.window。")

    def test_blur_switches_window_style(self):  # TC-07/08
        self.skipTest("悬浮窗内部的 blur/背景色读取方式未确认（窗口在屏幕外时 uitest dump -w 返回空节点）。")
