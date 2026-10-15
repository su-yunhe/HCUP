"""窗口几何信息：按窗口名从 hidumper 读取 [x y w h]。

适用于悬浮窗等不在 UI 树里的窗口。窗口名与 hidumper 输出的首列对应，
行尾可能带数字后缀（如 `cloudmusic0`），这里按“名称 + 可选数字”匹配。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import device


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def visible_fraction(self, screen_w: int, screen_h: int) -> float:
        """窗口落在屏幕内的面积占窗口总面积的比例，0 表示完全在屏幕外。"""
        if self.w <= 0 or self.h <= 0:
            return 0.0
        ix = max(0, min(self.x + self.w, screen_w) - max(self.x, 0))
        iy = max(0, min(self.y + self.h, screen_h) - max(self.y, 0))
        return (ix * iy) / (self.w * self.h)


# 首列窗口名，其后 8 个数字列（DisplayId Pid WinId Type Mode Flag ZOrd Orientation），再是 [x y w h]
_ROW = r"^{name}\d*\s+(?:-?\d+\s+){{8}}\[\s*(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s*\]"


def parse_window_rect(dump: str, name: str) -> Rect | None:
    match = re.search(_ROW.format(name=re.escape(name)), dump, re.M)
    if match is None:
        return None
    x, y, w, h = (int(g) for g in match.groups())
    return Rect(x, y, w, h)


def find_window_rect(device_sn: str, name: str) -> Rect | None:
    """返回名为 `name` 的窗口当前矩形；窗口不存在时返回 None。"""
    dump = device.shell(device_sn, "hidumper", "-s", "WindowManagerService", "-a", "-a")
    return parse_window_rect(dump, name)
