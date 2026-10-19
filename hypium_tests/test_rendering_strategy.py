"""场景三：渲染策略 SegmentButton 与策略胶囊（C1-C8）。"""
import numpy as np

from hypium_tests.sym_base import STRATEGIES, SymTestCase


class TestRenderingStrategy(SymTestCase):

    def test_01_default_single(self):
        """C1-C3/C6：三段从左到右 SINGLE/MULTIPLE_COLOR/MULTIPLE_OPACITY，默认选中 SINGLE。"""
        self.open_panel()
        seg = self.key("strategy_segment").getBounds()
        lefts = []
        for name in STRATEGIES:
            comp = self.require_text(name, f"缺少段 {name}", timeout=2)
            b = comp.getBounds()
            self.assertTrue(seg.top <= b.top and b.bottom <= seg.bottom, f"{name} 不在 SegmentButton 内")
            lefts.append(b.left)
        self.assertEqual(lefts, sorted(lefts))
        self.assertEqual(self.segment_selected(), ["SINGLE"])
        self.assertEqual(self.text_of("strategy_capsule"), "SINGLE")
        # 策略胶囊在 SegmentButton 下方
        self.assertGreaterEqual(self.bounds("strategy_capsule")[1], seg.bottom)

    def test_02_switch_updates_capsule(self):
        """C4/C6：切换后选中段与胶囊同步；重复点同一段幂等；收起再展开保持。"""
        self.open_panel()
        for name in ["MULTIPLE_COLOR", "MULTIPLE_OPACITY", "SINGLE", "MULTIPLE_OPACITY"]:
            self.pick_strategy(name)
            self.assertEqual(self.text_of("strategy_capsule"), name)
            self.assertEqual(self.segment_selected(), [name])
        self.pick_strategy("MULTIPLE_OPACITY")
        self.assertEqual(self.text_of("strategy_capsule"), "MULTIPLE_OPACITY")
        self.assertEqual(self.segment_selected(), ["MULTIPLE_OPACITY"])
        self.tap("ops_toggle", wait=0.8)
        self.open_panel()
        self.assertEqual(self.text_of("strategy_capsule"), "MULTIPLE_OPACITY")
        self.assertEqual(self.segment_selected(), ["MULTIPLE_OPACITY"])
        self.assertEqual(self.text_of("color_capsule_primary"), "accent", "切换策略不应改变颜色")

    def test_03_grid_renders_by_strategy(self):
        """C5/C8：主色 warning、副色 accent；SINGLE 只有主色，MULTIPLE_COLOR 出现副色，MULTIPLE_OPACITY 只有主色但外观不同。"""
        self.open_panel()
        self.pick("primary", "warning")
        self.pick("secondary", "accent")
        single = self.grid_image("single")
        self.assertLess(self.count_color(single, "accent"), 200, "SINGLE 下不应出现副色")
        self.pick_strategy("MULTIPLE_COLOR")
        multi = self.grid_image("multiple_color")
        self.assertGreater(self.count_color(multi, "accent"), 500, "MULTIPLE_COLOR 下应出现副色")
        self.assertGreater(self.count_color(multi, "warning"), 2000)
        self.pick_strategy("MULTIPLE_OPACITY")
        opacity = self.grid_image("multiple_opacity")
        self.assertLess(self.count_color(opacity, "accent"), 200, "MULTIPLE_OPACITY 下不应出现副色")
        self.assertGreater(self.count_color(opacity, "warning"), 2000)
        h = min(single.shape[0], opacity.shape[0])
        w = min(single.shape[1], opacity.shape[1])
        diff = np.abs(single[:h, :w].astype(np.int32) - opacity[:h, :w].astype(np.int32)).sum(axis=2)
        self.assertGreater(int((diff > 60).sum()), 1000, "MULTIPLE_OPACITY 与 SINGLE 渲染应不同")
        self.pick_strategy("SINGLE")
        back = self.grid_image("single_again")
        self.assertLess(self.count_color(back, "accent"), 200, "切回 SINGLE 后副色应消失")

    def test_04_strategy_capsule_copies_name(self):
        """C7：点击策略胶囊复制策略名。"""
        self.open_panel()
        self.pick_strategy("MULTIPLE_COLOR")
        self.driver.shell("hilog -r")
        self.tap("strategy_capsule", wait=1.0)
        log = self.driver.shell("hilog -x | grep 'Copied'")
        self.assertIn('Copied "MULTIPLE_COLOR"', log)
