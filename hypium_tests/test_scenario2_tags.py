"""场景二：历史 / 推荐标签搜索，最近 10 条、倒序、去重置顶、返回后排第一。"""
from hypium import BY

from hypium_tests.search_helpers import HISTORY_TAG, RECOMMEND_TAG, SearchTestCase


class TestScenario2Tags(SearchTestCase):

    def test_a16_a26_history_limit_10(self):
        """A16/A26：搜 11 个不同词后只显示最近 10 条，最早的被挤掉。"""
        self.open_search()
        words = [f"k{i}" for i in range(1, 12)]
        for w in words:
            self.search_and_back(w)
        items = self.wait_history("k11")
        self.assertEqual(items, list(reversed(words))[:10])
        self.assertNotIn("k1", items)
        self.assertIsNone(self.find_or_none(BY.key(f"{HISTORY_TAG}10"), timeout=1))

    def test_a17_a19_a21_a23_history_tag_click_moves_to_front(self):
        """A17/A19-A23：历史倒序；点非首个历史标签 → 填入搜索框并跳转 → 返回后该词排第一且不重复。"""
        self.open_search()
        for w in ("苹果", "香蕉", "橙子"):
            self.search_and_back(w)
        self.assertEqual(self.wait_history("橙子"), ["橙子", "香蕉", "苹果"])
        tag = self.require_component(BY.key(f"{HISTORY_TAG}2"), "第 3 个历史标签不存在")
        self.assertEqual(tag.getText(), "苹果")
        self.driver.click(tag)
        self.assertTrue(self.on_result_page(), "点历史标签后未进入结果页")
        self.assertEqual(self.result_keyword(), "苹果")
        self.back_to_search()
        self.assertEqual(self.input_value(), "苹果", "点历史标签应把该词填入搜索框")
        self.assertEqual(self.wait_history("苹果"), ["苹果", "橙子", "香蕉"])

    def test_a21_manual_input_existing_word_dedup(self):
        """A21/A43：手动输入已存在的词（带首尾空格）同样去重置顶；大小写不同算两个词。"""
        self.open_search()
        for w in ("Xiaomi", "手机"):
            self.search_and_back(w)
        self.search_and_back("  Xiaomi ")
        self.assertEqual(self.wait_history("Xiaomi"), ["Xiaomi", "手机"])
        self.search_and_back("xiaomi")
        self.assertEqual(self.wait_history("xiaomi"), ["xiaomi", "Xiaomi", "手机"])

    def test_a24_a25_recommend_tag_click(self):
        """A24/A25：点推荐标签 → 填入搜索框并跳转 → 返回后写入历史第一位。"""
        self.open_search()
        self.search_and_back("手机")
        rec = self.wait_recommend()
        self.require_precondition(rec is not None, "推荐词接口不可达（模拟器网络）")
        word = rec.getText()
        self.driver.click(rec)
        self.assertTrue(self.on_result_page(), "点推荐标签后未进入结果页")
        self.assertEqual(self.result_keyword(), word)
        self.back_to_search()
        self.assertEqual(self.input_value(), word, "点推荐标签应把该词填入搜索框")
        self.assertEqual(self.wait_history(word), [word, "手机"])
        # 推荐区域保持不变（返回时不重新请求，也不清空）
        self.assertEqual(self.find_or_none(BY.key(f"{RECOMMEND_TAG}0"), timeout=2).getText(), word)

    def test_a25_recommend_word_already_in_history(self):
        """A25 边界：推荐词已在历史中 → 移到最前，不重复。"""
        self.open_search()
        rec = self.wait_recommend()
        self.require_precondition(rec is not None, "推荐词接口不可达（模拟器网络）")
        word = rec.getText()
        self.search_and_back(word)
        self.search_and_back("手机")
        self.assertEqual(self.wait_history("手机"), ["手机", word])
        self.driver.click(self.require_component(BY.key(f"{RECOMMEND_TAG}0"), "推荐标签不存在"))
        self.assertTrue(self.on_result_page(), "点推荐标签后未进入结果页")
        self.back_to_search()
        self.assertEqual(self.wait_history(word), [word, "手机"])
