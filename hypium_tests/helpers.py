"""cmu-spec99 自测公共部分：应用重启、API 地址切换、搜索与列表滚动辅助。"""
from __future__ import annotations

import os
import shutil
import subprocess
import time

from hypium import BY, KeyCode

from harness.app import restart_app
from harness.driver import HarnessTestCase

BUNDLE = "cc.chenlvin.cloudmusic"
REAL_API = "http://192.168.1.97:3000"

LOAD_MORE = "点击加载更多"
NO_MORE = "没有更多了~"
K_INPUT = "search_input"
K_BUTTON = "search_button"
K_LOADING = "search_loading"
K_LIST = "search_result_list"
K_LOAD_MORE = "search_load_more"
K_LOADING_MORE = "search_loading_more"
K_NO_MORE = "search_no_more"
FOOTER_KEYS = (K_LOADING_MORE, K_LOAD_MORE, K_NO_MORE)

HDC = shutil.which("hdc") or "/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc"


def title_of(keyword: str) -> str:
    return f'"{keyword}" 的搜索结果'


class SearchTestBase(HarnessTestCase):
    """搜索结果分页用例的基类。子类在 setUpClass 里决定连真实服务器还是模拟服务。"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # 断言"不存在"很多，关掉隐式等待，统一用 find_or_none 的显式超时
        cls.driver.set_implicit_wait_time(0)
        cls.sn = cls.device_sn or os.environ.get("HDC_DEVICE") or cls.driver.device_sn

    @classmethod
    def hdc(cls, *args: str) -> str:
        out = subprocess.run([HDC, "-t", cls.sn, *args], capture_output=True, text=True, timeout=30)
        return (out.stdout or "") + (out.stderr or "")

    # ---------- 应用与设置 ----------

    def restart_to_index(self) -> None:
        restart_app(self.driver, BUNDLE, wait_time=2)
        self.require_component(BY.key(K_INPUT), "冷启动后未进入 Index（找不到 search_input）")

    def app_alive(self) -> bool:
        return bool(self.driver.shell(f"pidof {BUNDLE}").strip())

    def set_api_url(self, url: str) -> None:
        """Index → 更多 → 设置 → 打开"自定义API服务器地址"并填入 url → 返回 Index。不改源代码（U10）。"""
        inp = self.require_component(BY.key(K_INPUT), "不在 Index，无法进入设置")
        top = inp.getBounds().top
        heads = [b for b in (self.driver.find_all_components(BY.type("Button")) or []) if b.getBounds().bottom < top]
        self.assertTrue(heads, "找不到 Index 顶部按钮")
        more = max(heads, key=lambda b: b.getBounds().right)
        self.driver.click(more)
        self.driver.click(self.require_text("设置", "更多菜单里没有'设置'"))
        label = self.require_text("自定义API服务器地址", "设置页没有'自定义API服务器地址'")
        lb = label.getBounds()
        cy = (lb.top + lb.bottom) // 2
        toggles = self.driver.find_all_components(BY.type("Toggle")) or []
        self.assertTrue(toggles, "设置页找不到 Toggle")
        toggle = min(toggles, key=lambda t: abs((t.getBounds().top + t.getBounds().bottom) // 2 - cy))
        if not self.driver.get_component_property(toggle, "checked"):
            self.driver.click(toggle)
            self.driver.wait(0.8)
        field = self.require_type("TextInput", "打开开关后没有出现地址输入框")
        if field.getText() != url:
            self.driver.clear_text(field)
            self.driver.input_text(field, url)
            self.driver.wait(0.3)
        self.driver.click(self.require_component(BY.type("Button").text("设置"), "找不到'设置'按钮"))
        self.driver.wait(1)
        field = self.require_type("TextInput", "地址输入框消失")
        self.assertEqual(field.getText(), url, "API 地址没有设置成功")
        for _ in range(3):  # 第一次返回可能只是收起键盘
            self.driver.press_back()
            if self.find_or_none(BY.key(K_INPUT), timeout=2) is not None:
                return
        self.fail("从设置返回后不在 Index")

    # ---------- 搜索 ----------

    def type_keyword(self, keyword: str) -> None:
        inp = self.require_component(BY.key(K_INPUT), "找不到搜索框 search_input")
        self.driver.clear_text(inp)
        if keyword:
            self.driver.input_text(inp, keyword)
        self.driver.wait(0.3)

    def submit(self, enter: bool = False) -> None:
        if enter:
            self.driver.click(BY.key(K_INPUT))
            self.driver.press_key(KeyCode.ENTER)
        else:
            self.driver.click(self.require_component(BY.key(K_BUTTON), "找不到搜索按钮 search_button"))

    def search(self, keyword: str, enter: bool = False) -> None:
        self.type_keyword(keyword)
        self.submit(enter)
        self.require_text(title_of(keyword), f"没有进入搜索结果页：{keyword}")

    def wait_loaded(self, timeout: float = 20) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.driver.find_component(BY.key(K_LOADING)) is None:
                return
            self.driver.wait(0.3)
        self.fail("首页全屏加载一直没有结束")

    # ---------- 列表 ----------

    def exists(self, by) -> bool:
        return self.driver.find_component(by) is not None

    def has_text(self, text: str) -> bool:
        return self.exists(BY.text(text))

    def footer(self) -> str | None:
        for key in FOOTER_KEYS:
            if self.exists(BY.key(key)):
                return key
        return None

    def swipe_list(self, direction: str, distance: int = 80, swipe_time: float = 0.25) -> None:
        self.driver.swipe(direction, distance, area=BY.key(K_LIST), swipe_time=swipe_time)
        self.driver.wait(0.6)

    def scroll_to_bottom(self, max_swipes: int = 25) -> str:
        """一直上滑到列表底部出现加载/文案项，返回该项的 key。"""
        for _ in range(max_swipes):
            if self.footer() is None:
                self.swipe_list("UP")
                continue
            self.swipe_list("UP", 40)  # 再推一下，保证底部项完整可见
            f = self.footer()
            if f is not None:  # 推的过程中刚好追加完成时，底部项会被挤出屏幕，继续滑
                return f
        self.fail("滑动多次后仍未到达列表底部")

    def scroll_to_top(self, first_text: str, max_swipes: int = 25, watch_absent: str | None = None,
                      distance: int = 80) -> None:
        """一直下滑直到出现 first_text；watch_absent 不为空时，途中每一屏都断言该文本不存在。"""
        swipe_time = 0.25 if distance >= 60 else 0.8  # 找中间某首时慢滑，避免惯性滑过头
        for _ in range(max_swipes):
            if watch_absent is not None:
                self.assertFalse(self.has_text(watch_absent), f"滚动途中出现了不应存在的 {watch_absent!r}")
            if self.has_text(first_text):
                return
            self.swipe_list("DOWN", distance, swipe_time)
        self.fail(f"下滑多次后仍找不到 {first_text!r}")

    def click_load_more(self) -> None:
        self.driver.click(self.require_component(BY.key(K_LOAD_MORE), "找不到'点击加载更多'"))

    def assert_card(self, index: int, name: str) -> None:
        """序号为 index、歌名为 name 的卡片在当前屏（序号与歌名同一行，排除状态栏里的同名数字）。"""
        names = [c.getBounds() for c in (self.driver.find_all_components(BY.text(name)) or [])]
        self.assertTrue(names, f"当前屏找不到歌名 {name!r}")
        rows = [c.getBounds() for c in (self.driver.find_all_components(BY.text(str(index))) or [])]
        self.assertTrue(any(r.top < n.bottom + 60 and r.bottom > n.top - 60 and r.right <= n.left
                            for n in names for r in rows),
                        f"歌名 {name!r} 左侧的序号不是 {index}")

    def wait_loading_more_gone(self, timeout: float = 20) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.exists(BY.key(K_LOADING_MORE)):
                return
            self.driver.wait(0.3)
        self.fail("加载更多的加载指示一直没有消失")

    def wait_footer_not_loading(self, timeout: float = 20) -> str | None:
        """等加载更多结束，再滑到底返回底部项（追加后原底部项会被新歌曲挤出屏幕）。"""
        # 点击后'点击加载更多'应被加载指示替换；响应很快时可能观察不到，这里只等不断言
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and self.exists(BY.key(K_LOAD_MORE)):
            self.driver.wait(0.2)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.wait_loading_more_gone(timeout)
            f = self.scroll_to_bottom()
            if f != K_LOADING_MORE:
                return f
        self.fail("加载更多一直没有结束")

    def load_more_and_wait(self) -> str | None:
        self.click_load_more()
        return self.wait_footer_not_loading()

    def dismiss_error_dialog(self, timeout: float = 8) -> bool:
        ok = self.find_or_none(BY.text("确定"), timeout=timeout)
        if ok is None:
            return False
        self.assertTrue(self.has_text("网络请求出错"), "出现了'确定'但不是网络错误弹窗")
        self.driver.click(ok)
        self.driver.wait(0.8)
        return True
