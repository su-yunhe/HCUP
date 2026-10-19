"""场景二：颜色重置（B1-B8）。"""
from hypium_tests.sym_base import SymTestCase


class TestColorReset(SymTestCase):

    def assert_default_colors(self):
        self.assertEqual(self.text_of("color_capsule_primary"), "accent")
        self.assertEqual(self.text_of("color_capsule_secondary"), "connected")
        self.assertEqual(self.text_of("color_capsule_background"), "undefined")

    def test_01_reset_restores_defaults(self):
        """B2-B5：主色 accent、副色 connected、背景色 undefined，网格回到默认色。"""
        self.open_panel()
        self.assert_default_colors()  # B6：冷启动即默认值
        self.pick("primary", "warning")
        self.pick("secondary", "alert")
        self.pick("background", "foreground")
        self.assertEqual(self.text_of("color_capsule_background"), "foreground")
        self.tap("color_reset")
        self.assert_default_colors()
        img = self.grid_image("reset")
        self.assertGreater(self.count_color(img, "accent"), 2000, "重置后网格应回到 accent")
        self.assertLess(self.count_color(img, "warning"), 200)

    def test_02_reset_only_colors(self):
        """B7/U-10：重置不影响策略、搜索词、选中项和面板展开状态。"""
        self.search("wifi")
        glyphs = self.grid_glyphs()
        self.assertGreater(len(glyphs), 0)
        self.driver.click(glyphs[0])
        self.driver.wait(0.5)
        no_text = self.text_of("info_no")
        self.open_panel()
        self.pick_strategy("MULTIPLE_COLOR")
        self.pick("primary", "warning")
        self.tap("color_reset")
        self.assert_default_colors()
        self.assertEqual(self.text_of("strategy_capsule"), "MULTIPLE_COLOR")
        self.assertEqual(self.segment_selected(), ["MULTIPLE_COLOR"])
        self.assertEqual(self.text_of("search_input"), "wifi")
        self.assertEqual(self.text_of("info_no"), no_text)
        self.assertIsNotNone(self.key_or_none("ops_panel"), "重置后面板应保持展开")

    def test_03_reset_idempotent(self):
        """边界：默认状态下点重置、连点重置均幂等。"""
        self.open_panel()
        self.tap("color_reset")
        self.assert_default_colors()
        self.pick("primary", "alert")
        for _ in range(3):
            self.driver.click(self.key("color_reset"))
        self.driver.wait(0.8)
        self.assert_default_colors()

    def test_04_search_reset_keeps_colors(self):
        """B8：搜索栏重置只清空搜索，不重置颜色/策略。"""
        self.open_panel()
        self.pick("primary", "warning")
        self.pick_strategy("MULTIPLE_OPACITY")
        self.search("wifi")
        few = len(self.grid_glyphs())
        self.tap("search_reset", wait=1.0)
        self.assertEqual(self.text_of("search_input"), "")
        self.assertGreater(len(self.grid_glyphs()), few, "搜索重置后应显示全部符号")
        self.assertEqual(self.text_of("color_capsule_primary"), "warning")
        self.assertEqual(self.text_of("strategy_capsule"), "MULTIPLE_OPACITY")
