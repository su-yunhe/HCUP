"""测试运行器：发现并执行某道题目录下的测试文件，汇总统一格式的报告。

用法：
    python -m harness.runner --project <本题工程目录> [--device <序列号>] [--json out.json]

约定：被测项目目录下的 `hypium_tests/test_*.py` 为该题的测试文件，
其中的测试类应继承 `harness.driver.HarnessTestCase`。
"""
from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

from . import device as device_mod
from . import env_check
from .report import RecordingResult, RunReport


def discover(project_dir: Path) -> unittest.TestSuite:
    tests_dir = project_dir / "hypium_tests"
    if not tests_dir.is_dir():
        raise FileNotFoundError(
            f"未找到测试目录: {tests_dir}；请在该题工作目录下创建 hypium_tests/test_*.py"
        )
    loader = unittest.TestLoader()
    return loader.discover(start_dir=str(tests_dir), pattern="test_*.py", top_level_dir=str(project_dir))


def _collect_case_names(suite: unittest.TestSuite) -> list[str]:
    names = []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            names.extend(_collect_case_names(test))
        else:
            names.append(str(test))
    return names


def _inject_device_sn(suite: unittest.TestSuite, device_sn: str) -> None:
    """把设备序列号注入每个 HarnessTestCase 子类，供 setUpClass 使用。"""
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            _inject_device_sn(test, device_sn)
        else:
            test.__class__.device_sn = device_sn


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="本题工程目录（绝对路径）")
    parser.add_argument("--device", default=None, help="设备序列号，省略则要求唯一在线设备")
    parser.add_argument("--json", default=None, help="将报告另存为 JSON 文件的路径")
    parser.add_argument("--skip-env-check", action="store_true", help="跳过环境规格校验")
    args = parser.parse_args(argv)

    project_dir = Path(args.project).resolve()
    device_sn = device_mod.select_device(args.device)

    env_warnings: list[str] = []
    if not args.skip_env_check:
        env_warnings = env_check.check(device_sn).warnings

    suite = discover(project_dir)
    case_names = _collect_case_names(suite)
    _inject_device_sn(suite, device_sn)

    runner = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult)
    result = runner.run(suite)

    report = RunReport(
        project=str(project_dir),
        device_sn=device_sn,
        env_warnings=env_warnings,
        cases=result.to_cases(case_names),
    )
    report.print_summary()

    if args.json:
        Path(args.json).write_text(report.to_json(), encoding="utf-8")
        print(f"\n报告已保存: {args.json}")

    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
