"""场景五/六：信息栏水平滚动与布局隔离（E1-E5、F1-F5），回归保护。"""
from hypium_tests.sym_base import SymTestCase

LONG_NAME = "headphones_badge_checkmark_shield_filled_battery_filled"


class TestInfoBar(SymTestCase):

    def slide_info(self, to_left: bool = True):
        s = self.key("info_scroll").getBounds()
        y = (s.top + s.bottom) // 2
        a, b = (s.right - 40, y), (s.left + 40, y)
        self.driver.slide(a if to_left else b, b if to_left else a, slide_time=0.4)
        self.driver.wait(1.0)

    def select_by_search(self, name: str):
        self.search(name)
        glyphs = self.grid_glyphs()
        self.assertGreater(len(glyphs), 0, f"搜索 {name} 无结果")
        self.driver.click(glyphs[0])
        self.driver.wait(0.8)

    def layout_bounds(self):
        return [self.bounds(k) for k in ("search_input", "symbol_grid", "info_scroll")]

    def test_01_default_four_capsules(self):
        """E1：冷启动四个胶囊依次为 No./字符/Unicode/名称。"""
        self.assertEqual(self.text_of("info_no"), "No. 0")
        self.assertEqual(self.text_of("info_unicode"), "U+000020")
        xs = [self.bounds(k)[0] for k in ("info_no", "info_char", "info_unicode")]
        self.assertEqual(xs, sorted(xs))
        grid, info, search = self.bounds("symbol_grid"), self.bounds("info_scroll"), self.bounds("search_input")
        self.assertTrue(grid[3] <= info[1] <= info[3] <= search[1], "信息栏应位于网格下方、搜索栏上方")

    def test_02_long_name_scrolls_fully_visible(self):
        """E2/E3/E5：长名称左滑后完整可见，右滑回到 No.。"""
        self.select_by_search(LONG_NAME)
        self.assertEqual(self.text_of("info_no"), "No. 644")
        self.slide_info(to_left=True)
        self.slide_info(to_left=True)
        name = self.key("info_name")
        self.assertEqual(name.getText(), LONG_NAME)
        nb, sb = name.getBounds(), self.key("info_scroll").getBounds()
        self.assertTrue(sb.left <= nb.left and nb.right <= sb.right, f"名称胶囊未完整可见: {nb} / {sb}")
        self.slide_info(to_left=False)
        self.slide_info(to_left=False)
        self.assertEqual(self.text_of("info_no"), "No. 644")

    def test_03_horizontal_swipe_does_not_scroll_grid(self):
        """F1：信息栏横滑时网格不动。"""
        before = [g.getBounds() for g in self.grid_glyphs()[:3]]
        self.slide_info(to_left=True)
        after = [g.getBounds() for g in self.grid_glyphs()[:3]]
        self.assertEqual([str(b) for b in before], [str(b) for b in after], "横滑信息栏带动了网格")
        self.assertTrue(self.key_or_none("info_name") is not None, "横滑后名称胶囊应进入视口")

    def test_04_vertical_grid_scroll_keeps_info_bar(self):
        """F2：纵滑网格不影响信息栏。"""
        info_before = self.bounds("info_scroll")
        no_before = self.text_of("info_no")
        g = self.key("symbol_grid").getBounds()
        cx = (g.left + g.right) // 2
        self.driver.slide((cx, g.bottom - 60), (cx, g.top + 60), slide_time=0.4)
        self.driver.wait(1.0)
        self.assertEqual(self.bounds("info_scroll"), info_before)
        self.assertEqual(self.text_of("info_no"), no_before)

    def test_05_layout_independent_of_name_width(self):
        """F3/F4/F5：短名称与长名称下搜索栏、网格、信息栏位置一致；展开面板后同样一致。"""
        self.select_by_search("wifi")
        short = self.layout_bounds()
        self.select_by_search(LONG_NAME)
        self.assertEqual(self.layout_bounds(), short, "面板收起：布局随名称宽度变化")
        grid = self.bounds("symbol_grid")
        self.assertGreater(grid[3] - grid[1], (short[2][3] - short[2][1]) * 5, "网格应占主体空间")
        self.open_panel()
        long_open = self.layout_bounds()
        self.tap("search_reset", wait=1.0)
        self.select_by_search("wifi")
        self.assertEqual(self.layout_bounds(), long_open, "面板展开：布局随名称宽度变化")
        self.assertGreater(len(self.grid_glyphs()), 0, "面板展开后网格仍应可见")
