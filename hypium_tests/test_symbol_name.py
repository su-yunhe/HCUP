"""场景四：名称拼写修正 kmark_on_bookmark → bookmark_on_bookmark（D1-D5），以及搜索边界。"""
from hypium_tests.sym_base import SymTestCase

NAME = "bookmark_on_bookmark"


class TestSymbolName(SymTestCase):

    def swipe_info_left(self):
        s = self.key("info_scroll").getBounds()
        y = (s.top + s.bottom) // 2
        self.driver.slide((s.right - 40, y), (s.left + 40, y), slide_time=0.4)
        self.driver.wait(1.0)

    def test_01_search_correct_name(self):
        """D2/D3/D5：搜索正确名称恰好 1 项，渲染非空白，选中后信息栏显示正确信息。"""
        self.search(NAME)
        glyphs = self.grid_glyphs()
        self.assertEqual(len(glyphs), 1, f"搜索 {NAME} 应恰好 1 项")
        img = self.grid_image("bookmark")
        self.assertGreater(self.count_color(img, "accent"), 300, "按名称引用的符号应能正常渲染（非空白）")
        self.driver.click(glyphs[0])
        self.driver.wait(0.8)
        self.assertEqual(self.text_of("info_no"), "No. 476")
        self.assertEqual(self.text_of("info_unicode"), "U+0F01E2")
        self.swipe_info_left()
        self.assertEqual(self.text_of("info_name"), NAME)

    def test_02_case_and_old_name(self):
        """D2/D4：大写也命中；旧名作为子串仍命中修正后的同一项。"""
        self.search(NAME.upper())
        self.assertEqual(len(self.grid_glyphs()), 1)
        self.search("kmark_on_bookmark")
        glyphs = self.grid_glyphs()
        self.assertEqual(len(glyphs), 1)
        self.driver.click(glyphs[0])
        self.driver.wait(0.8)
        self.swipe_info_left()
        self.assertEqual(self.text_of("info_name"), NAME)

    def test_03_empty_and_blank_input(self):
        """边界：纯空格无结果不崩溃、面板仍可用；空输入回车显示全部。"""
        self.search("   ")
        self.assertEqual(len(self.grid_glyphs()), 0, "纯空格应无结果（基线不 trim）")
        self.open_panel()
        self.pick("primary", "warning")
        self.assertEqual(self.text_of("color_capsule_primary"), "warning")
        self.tap("search_reset", wait=1.0)
        self.search("")
        self.assertGreater(len(self.grid_glyphs()), 10, "空输入回车应显示全部符号")
        self.assertGreater(self.count_color(self.grid_image("all"), "warning"), 2000,
                           "重新出现的符号应使用当前颜色")
