"""应用生命周期与导航辅助。与具体赛题无关，包名和页面文案由各题测试传入。"""
from __future__ import annotations

import time

from hypium import BY

DEFAULT_TIMEOUT = 15


def restart_app(driver, bundle: str, wait_time: float = 2) -> None:
    """强制停止后冷启动，等价于“完全退出再重新打开”。

    签名取自 Hypium 6.1.0.210（stop_app / start_app），尚未在设备上实测；
    首次使用时请确认 start_app 不带 page_name 时能拉起主 Ability。
    """
    driver.stop_app(bundle)
    driver.start_app(bundle, wait_time=wait_time)


def click_text_path(driver, texts: list[str], timeout: float = DEFAULT_TIMEOUT) -> None:
    """依次点击一串文案，用于从某个起点页逐级导航到目标页。

    每一步都等待目标文案出现；找不到时抛 AssertionError 并指出卡在哪一步。
    """
    for text in texts:
        deadline = time.monotonic() + timeout
        component = None
        while time.monotonic() < deadline:
            component = driver.find_component(BY.text(text))
            if component is not None:
                break
            driver.wait(0.5)
        if component is None:
            raise AssertionError(f"导航失败：{timeout}s 内未找到文案 {text!r}")
        driver.click(component)
        driver.wait(0.5)
