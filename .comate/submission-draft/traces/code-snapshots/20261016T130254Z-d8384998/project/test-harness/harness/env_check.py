"""环境校验：对照 docs/development.md 中"正式评测与自测模拟器配置"一节，
检查当前连接设备的系统版本、屏幕参数是否与官方评测环境一致。

校验结果仅用于提示偏差，不阻塞测试执行——
文档原文强调"本地自测通过不代表正式测试通过"，环境校验的作用是降低偏差，不是替代正式评测。
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

from . import device

# 官方评测环境规格，来源：docs/development.md 第93-103行"正式评测与自测模拟器配置"
OFFICIAL_SPEC = {
    "model": "Pura 90 Pro Max",
    "config": "PHEMU-FD00",
    "os_version": "6.1.0",
    "api_version": "23",
    "image_version": "6.1.0.115",
    "resolution": (1308, 2880),
    "dpi": 560,
}


@dataclass
class EnvCheckResult:
    device_sn: str
    software_version: str | None
    resolution: tuple[int, int] | None
    warnings: list[str]

    @property
    def matches_official(self) -> bool:
        return not self.warnings


def _get_software_version(device_sn: str) -> str | None:
    try:
        out = device.shell(
            device_sn, "param", "get", "const.product.software.version"
        )
    except Exception:
        return None
    return out.strip() or None


def _get_resolution(device_sn: str) -> tuple[int, int] | None:
    """从 hidumper 的窗口信息里解析屏幕分辨率（取 SCBDesktop/桌面窗口的 w/h）。"""
    try:
        out = device.shell(
            device_sn, "hidumper", "-s", "WindowManagerService", "-a", "-a"
        )
    except Exception:
        return None
    # 形如: "...[ 0    0    1308 2880 ] [ ... ]"，取第一条分辨率合理的记录
    for match in re.finditer(r"\[\s*\d+\s+\d+\s+(\d+)\s+(\d+)\s*\]", out):
        w, h = int(match.group(1)), int(match.group(2))
        if w > 0 and h > 0:
            return (w, h)
    return None


def check(device_sn: str) -> EnvCheckResult:
    warnings: list[str] = []

    software_version = _get_software_version(device_sn)
    if software_version is None:
        warnings.append("无法读取设备系统版本（const.product.software.version）。")
    elif OFFICIAL_SPEC["image_version"] not in software_version:
        warnings.append(
            f"系统镜像版本为 {software_version!r}，"
            f"官方评测使用 {OFFICIAL_SPEC['image_version']}（API {OFFICIAL_SPEC['api_version']}）。"
        )

    resolution = _get_resolution(device_sn)
    if resolution is None:
        warnings.append("无法读取设备屏幕分辨率。")
    elif resolution != OFFICIAL_SPEC["resolution"]:
        warnings.append(
            f"屏幕分辨率为 {resolution}，官方评测使用 "
            f"{OFFICIAL_SPEC['resolution']}（{OFFICIAL_SPEC['model']} / "
            f"{OFFICIAL_SPEC['config']}）。请在 DevEco Studio Device Manager 中确认模拟器机型。"
        )

    return EnvCheckResult(
        device_sn=device_sn,
        software_version=software_version,
        resolution=resolution,
        warnings=warnings,
    )


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default=None, help="设备序列号，省略则要求唯一在线设备")
    args = parser.parse_args()

    device_sn = device.select_device(args.device)
    result = check(device_sn)

    print(f"设备: {result.device_sn}")
    print(f"系统版本: {result.software_version}")
    print(f"屏幕分辨率: {result.resolution}")
    print(
        f"官方评测环境: {OFFICIAL_SPEC['model']} / {OFFICIAL_SPEC['config']} / "
        f"HarmonyOS {OFFICIAL_SPEC['os_version']}（API {OFFICIAL_SPEC['api_version']}）/ "
        f"镜像 {OFFICIAL_SPEC['image_version']} / {OFFICIAL_SPEC['resolution']} @ {OFFICIAL_SPEC['dpi']}dpi"
    )
    if result.matches_official:
        print("✓ 环境与官方评测规格一致。")
    else:
        print("⚠ 发现以下偏差（不阻塞测试，仅供参考）：")
        for w in result.warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    _main()
