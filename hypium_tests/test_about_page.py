"""jm-spec35「关于页面展示应用图标和版本号」本地自测用例。

依据本工程 spec/requirement.md 编写，不是官方评测用例。

运行（在本工程 logs/ 下执行，Hypium 生成的 reports/ 会落在这里）：
    COMMON=/Users/bress/Documents/code/harmonycup-work/common
    cd logs && PYTHONPATH="$COMMON/test-harness" "$COMMON/.venv/bin/python" -m harness.runner \
        --project "$(cd .. && pwd)" --device <设备序列号>

前置：本题 HAP 已安装（同 bundleName 的其他题会互相覆盖，跑之前务必重装本题产物）；
用例会冷启动应用，必要时点击隐私确认“同意”，再从首页出发。
"""
from __future__ import annotations

import re

from hypium import BY

from harness import device
from harness.driver import HarnessTestCase

BUNDLE = "com.hefengbao.jingmo.hw"
ABILITY = "EntryAbility"
HOME_TITLE = "京墨文库"


def installed_version_name(device_sn: str) -> str:
    """读取已安装包的 versionName（bm dump 中第一个非空值即应用级版本名）。"""
    output = device.shell(device_sn, "bm", "dump", "-n", BUNDLE)
    for value in re.findall(r'"versionName":\s*"([^"]*)"', output):
        if value:
            return value
    raise AssertionError(f"未能从 bm dump 读取 {BUNDLE} 的 versionName")


class AboutPageTest(HarnessTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.version_name = installed_version_name(cls.driver.device_sn)

    def setUp(self) -> None:
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, ABILITY, wait_time=3)
        # 首次启动（或重新安装后）会出现隐私确认，同意后进入首页
        agree = self.find_or_none(BY.text("同意"), timeout=3)
        if agree is not None:
            self.driver.click(agree)
            self.driver.wait(2)
        self.require_text(HOME_TITLE, "冷启动后应停留在首页。")

    def open_settings(self) -> None:
        for _ in range(3):
            self.driver.wait(1)
            title = self.require_text(HOME_TITLE, "首页应显示标题。").getBounds()
            center_y = (title.top + title.bottom) // 2
            images = self.driver.find_all_components(BY.type("Image")) or []
            candidates = [img for img in images
                          if img.getBounds().top <= center_y <= img.getBounds().bottom]
            self.assertTrue(candidates, "首页标题栏应有设置图标。")
            settings_icon = max(candidates, key=lambda img: img.getBounds().right)
            self.driver.click(settings_icon)
            if self.find_or_none(BY.text("关于"), timeout=5) is not None:
                return
        self.fail("点击设置图标后应进入设置页。")

    def open_about(self) -> None:
        about = self.require_text("关于", "设置页应有“关于”选项。")
        self.driver.click(about)
        self.require_component(BY.key("about_app_icon"), "关于页应显示应用图标。")
        self.driver.wait(1)  # 等待转场动画结束，避免读取到正在销毁/移动的节点

    def snapshot(self, by) -> list[tuple[str, object]]:
        """读取当前匹配组件的 (text, bounds)，忽略读取瞬间已消失的节点。"""
        result = []
        for component in self.driver.find_all_components(by) or []:
            try:
                result.append((component.getText() or "", component.getBounds()))
            except Exception:  # 节点在读取期间被销毁（如状态栏刷新）
                continue
        return result

    def assert_icon_and_version(self) -> None:
        icon = self.require_component(BY.key("about_app_icon"), "关于页应显示应用图标。")
        version = self.require_text(self.version_name, f"关于页应显示版本名称 {self.version_name}。")
        ib, vb = icon.getBounds(), version.getBounds()
        width, height = ib.right - ib.left, ib.bottom - ib.top
        self.assertGreater(width, 0, "图标应可见。")
        self.assertLessEqual(abs(width - height), 2, "圆形图标宽高应相等。")
        self.assertGreaterEqual(vb.top, ib.bottom, "版本名称应位于图标下方。")
        icon_cx, version_cx = (ib.left + ib.right) / 2, (vb.left + vb.right) / 2
        self.assertLessEqual(abs(icon_cx - version_cx), 4, "版本名称应与图标水平居中对齐。")
        self.assertEqual(version.getText(), self.version_name, "版本文本应与安装包 versionName 完全一致。")
        # 图标位于页面内容顶部：导航标题“关于”与图标之间不应有其他正文文本
        # （Navigation 下层的设置页仍在 UI 树中，其“关于”条目也会被找到，故取图标上方的那个）
        self.require_text("关于", "关于页应显示标题。")
        titles = [b for _, b in self.snapshot(BY.text("关于")) if b.bottom <= ib.top]
        self.assertTrue(titles, "图标应位于导航标题下方的内容区顶部。")
        title = max(titles, key=lambda b: b.bottom)
        above = [text for text, b in self.snapshot(BY.type("Text"))
                 if text and b.top >= title.bottom and b.bottom <= ib.top]
        self.assertFalse(above, f"图标应位于内容顶部，上方出现文本：{above}")

    def test_icon_and_version_shown(self):  # 场景一 步骤1-3 / 场景二
        self.open_settings()
        self.open_about()
        self.assert_icon_and_version()

    def test_existing_content_kept(self):  # 场景一 步骤4
        self.open_settings()
        self.open_about()
        self.require_text("❤贺丰宝（hefengbao）设计和编码❤", "应保留作者信息。")
        texts = [text for text, _ in self.snapshot(BY.type("Text"))]
        desc = next((t for t in texts if "京墨文库" in t and "源码仓库" in t), "")
        self.assertIn("https://github.com/hefengbao/jingmo-for-HarmonyOS", desc, "简介应包含 GitHub 仓库地址。")
        self.assertIn("https://gitee.com/hefengbao/jingmo-for-HarmonyOS", desc, "简介应包含 Gitee 仓库地址。")
        self.driver.swipe("UP")
        self.driver.wait(1)
        self.require_text("公众号：NowInLife", "应保留公众号信息。")

    def test_reenter_keeps_consistent(self):  # 返回与重复进入
        self.open_settings()
        for _ in range(3):
            self.open_about()
            self.assert_icon_and_version()
            self.driver.press_back()
            self.driver.wait(1)
            self.require_text("关于", "返回后应回到设置页。")
            self.assertIsNone(self.driver.find_component(BY.key("about_app_icon")), "返回后关于页应已关闭。")
        self.driver.press_back()
        self.require_text(HOME_TITLE, "再次返回应回到首页。")
