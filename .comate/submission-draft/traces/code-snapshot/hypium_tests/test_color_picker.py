"""场景一：'^' 入口、操作面板、三组颜色选择器、胶囊显示名称（A1-A13）。"""
from hypium import BY

from hypium_tests.sym_base import COLOR_NAMES, STRATEGIES, SymTestCase

GROUPS = ["primary", "secondary", "background"]


class TestColorPicker(SymTestCase):

    def test_01_toggle_present_and_panel_collapsed(self):
        """A1/A2：冷启动有可点击的 '^'，面板默认收起。"""
        toggle = self.key("ops_toggle")
        self.assertTrue(toggle.isClickable(), "'^' 不可点击")
        self.assertIsNone(self.key_or_none("ops_panel"), "冷启动时面板不应展开")
        for text in ["主色", "副色", "背景色"] + STRATEGIES:
            self.assertIsNone(self.driver.find_component(BY.text(text)), f"收起状态不应出现 {text}")
        # '^' 在搜索行最右侧
        self.assertGreater(self.bounds("ops_toggle")[0], self.bounds("search_reset")[2])

    def test_02_expand_shows_three_groups(self):
        """A3/A5/A6/A11/B1/C1：展开后三组颜色、6 个圆点、胶囊、重置图标、SegmentButton。"""
        self.open_panel()
        tops = []
        for group, label in zip(GROUPS, ["主色", "副色", "背景色"]):
            row = self.key(f"color_group_{group}")
            tops.append(row.getBounds().top)
            self.require_text(label, f"缺少标签 {label}", timeout=2)
            lefts = []
            for name in COLOR_NAMES:
                dot = self.key(f"color_dot_{group}_{name}")
                self.assertTrue(dot.isClickable(), f"{group}/{name} 圆点不可点击")
                lefts.append(dot.getBounds().left)
            self.assertEqual(lefts, sorted(lefts), "圆点顺序不对")
        self.assertEqual(tops, sorted(tops), "三组应按 主色/副色/背景色 从上到下")
        self.assertEqual(self.text_of("color_capsule_primary"), "accent")
        self.assertEqual(self.text_of("color_capsule_secondary"), "connected")
        self.assertEqual(self.text_of("color_capsule_background"), "undefined")
        self.assertTrue(self.key("color_reset").isClickable())
        for name in STRATEGIES:
            self.require_text(name, f"SegmentButton 缺少段 {name}", timeout=2)
        # 面板不打乱信息栏：信息栏仍是第一个 Scroll，前 4 个 Button 仍是信息胶囊
        self.assertEqual(self.driver.find_component(BY.type("Scroll")).getId(), "info_scroll")
        first_buttons = [b.getId() for b in self.driver.find_all_components(BY.type("Button"))[:4]]
        self.assertEqual(first_buttons, ["info_no", "info_char", "info_unicode", "info_name"])

    def test_03_pick_primary_recolors_grid(self):
        """A7/A10：选主色后胶囊为该色名，网格立即换色。"""
        self.open_panel()
        before = self.grid_image("before")
        self.assertGreater(self.count_color(before, "accent"), 2000, "默认主色应为 accent")
        self.pick("primary", "warning")
        self.assertEqual(self.text_of("color_capsule_primary"), "warning")
        after = self.grid_image("after")
        self.assertGreater(self.count_color(after, "warning"), 2000, "网格未换成 warning")
        self.assertLess(self.count_color(after, "accent"), 200, "SINGLE 下网格不应残留 accent")

    def test_04_pick_secondary_and_background(self):
        """A8/A9：副色、背景色各自独立更新胶囊，互不影响。"""
        self.open_panel()
        self.pick("secondary", "alert")
        self.assertEqual(self.text_of("color_capsule_secondary"), "alert")
        self.assertEqual(self.text_of("color_capsule_primary"), "accent")
        self.assertEqual(self.text_of("color_capsule_background"), "undefined")
        self.pick("background", "handup")
        self.assertEqual(self.text_of("color_capsule_background"), "handup")
        self.assertEqual(self.text_of("color_capsule_secondary"), "alert")

    def test_05_repeat_and_rapid_clicks(self):
        """边界：重复点同一圆点幂等；连点不同圆点以最后一次为准。"""
        self.open_panel()
        for _ in range(3):
            self.pick("primary", "connected")
        self.assertEqual(self.text_of("color_capsule_primary"), "connected")
        for name in ["warning", "alert", "foreground"]:
            self.driver.click(self.key(f"color_dot_secondary_{name}"))
        self.driver.wait(0.8)
        self.assertEqual(self.text_of("color_capsule_secondary"), "foreground")

    def test_06_toggle_collapse_keeps_values(self):
        """A4/U-14：再次点 '^' 收起，颜色保留；再展开胶囊仍为原值；连点按奇偶切换。"""
        self.open_panel()
        self.pick("primary", "warning")
        self.tap("ops_toggle", wait=0.8)
        self.assertIsNone(self.key_or_none("ops_panel"), "再次点击 '^' 应收起面板")
        self.assertIsNotNone(self.key_or_none("ops_toggle"), "收起后 '^' 应仍在")
        self.assertGreater(self.count_color(self.grid_image("collapsed"), "warning"), 2000,
                           "收起面板后网格应保持自定义颜色")
        for _ in range(3):
            self.driver.click(self.key("ops_toggle"))
        self.driver.wait(1.0)
        self.key("ops_panel")
        self.assertEqual(self.text_of("color_capsule_primary"), "warning")

    def test_07_new_items_use_current_color(self):
        """A10：滚动加载的项、搜索结果项都用当前颜色。"""
        self.open_panel()
        self.pick("primary", "warning")
        g = self.key("symbol_grid").getBounds()
        cx = (g.left + g.right) // 2
        self.driver.slide((cx, g.bottom - 60), (cx, g.top + 60), slide_time=0.4)
        self.driver.wait(1.0)
        img = self.grid_image("scrolled")
        self.assertGreater(self.count_color(img, "warning"), 2000, "滚动后新出现的项颜色不对")
        self.assertLess(self.count_color(img, "accent"), 200)
        self.search("bookmark")
        self.assertGreater(len(self.grid_glyphs()), 0, "搜索 bookmark 应有结果")
        img = self.grid_image("search")
        self.assertGreater(self.count_color(img, "warning"), 500, "搜索结果颜色不对")
        self.assertLess(self.count_color(img, "accent"), 200)
        self.assertEqual(self.text_of("color_capsule_primary"), "warning", "搜索不应改变颜色")

    def test_08_capsule_copies_color_name(self):
        """A12：点击颜色胶囊把名称写入剪贴板（hilog 记录）。"""
        self.open_panel()
        self.pick("secondary", "warning")
        self.driver.shell("hilog -r")
        self.tap("color_capsule_secondary", wait=1.0)
        log = self.driver.shell("hilog -x | grep 'Copied'")
        self.assertIn('Copied "warning"', log, "点击胶囊未复制颜色名称")
