"""设备发现与连接：封装 hdc 调用，和题包 Hypium 示例保持一致的选择逻辑。"""
from __future__ import annotations

import shutil
import subprocess


class DeviceError(RuntimeError):
    """hdc 不可用、设备数量不符合预期等场景下抛出。"""


def find_hdc() -> str:
    """定位 hdc 可执行文件。要求调用方已将 DevEco SDK 的
    openharmony/toolchains 目录加入 PATH（见 docs/development.md）。
    """
    hdc = shutil.which("hdc") or shutil.which("hdc_std")
    if hdc is None:
        raise DeviceError(
            "未找到 hdc，请将 DevEco Studio 自带的 "
            "openharmony/toolchains 目录加入 PATH。"
        )
    return hdc


def list_targets() -> list[str]:
    """返回 `hdc list targets` 报告的已连接设备序列号列表（过滤空槽位）。"""
    hdc = find_hdc()
    result = subprocess.run(
        [hdc, "list", "targets"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and "[Empty]" not in line
    ]


def select_device(requested: str | None = None) -> str:
    """选定要连接的设备序列号。

    - 指定了 `requested`：校验它确实在线。
    - 未指定：要求当前只有一台设备在线，否则报错（避免误连错设备）。
    """
    devices = list_targets()
    if requested:
        if requested not in devices:
            raise DeviceError(f"指定设备未连接：{requested}；当前在线设备：{devices}")
        return requested
    if len(devices) != 1:
        raise DeviceError(
            f"需要连接恰好一台设备，或通过 --device 明确指定；当前在线设备：{devices}"
        )
    return devices[0]


def shell(device_sn: str, *args: str, timeout: float = 10) -> str:
    """在指定设备上执行一条 `hdc shell` 命令，返回标准输出文本。"""
    hdc = find_hdc()
    result = subprocess.run(
        [hdc, "-t", device_sn, "shell", *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout,
    )
    return result.stdout
