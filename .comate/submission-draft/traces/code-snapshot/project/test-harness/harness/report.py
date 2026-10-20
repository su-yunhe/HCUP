"""统一的测试结果报告格式：终端摘要 + 可选 JSON 文件。

结果分四类：pass / fail / error / skip。
skip 表示“没有被验证”（前置条件不满足、占位用例等），既不算通过也不算失败，
但摘要里会单独列出，避免把未执行的用例误读成绿色。
"""
from __future__ import annotations

import json
import unittest
from dataclasses import asdict, dataclass, field

PASS, FAIL, ERROR, SKIP = "pass", "fail", "error", "skip"
_MARKS = {PASS: "✓", FAIL: "✗", ERROR: "✗", SKIP: "-"}


@dataclass
class CaseResult:
    name: str
    outcome: str  # PASS | FAIL | ERROR | SKIP
    message: str = ""


@dataclass
class RunReport:
    project: str
    device_sn: str
    env_warnings: list[str] = field(default_factory=list)
    cases: list[CaseResult] = field(default_factory=list)

    def _count(self, *outcomes: str) -> int:
        return sum(1 for c in self.cases if c.outcome in outcomes)

    @property
    def passed(self) -> int:
        return self._count(PASS)

    @property
    def failed(self) -> int:
        return self._count(FAIL, ERROR)

    @property
    def skipped(self) -> int:
        return self._count(SKIP)

    def print_summary(self) -> None:
        print(f"\n项目: {self.project}")
        print(f"设备: {self.device_sn}")
        if self.env_warnings:
            print("环境偏差提示:")
            for w in self.env_warnings:
                print(f"  - {w}")
        print(
            f"\n测试用例: {len(self.cases)}  通过: {self.passed}  "
            f"失败: {self.failed}  跳过(未验证): {self.skipped}"
        )
        for c in self.cases:
            print(f"  {_MARKS[c.outcome]} {c.name}" + (f" — {c.message}" if c.message else ""))
        if self.skipped:
            print(f"\n注意: 有 {self.skipped} 个用例被跳过，这些行为没有被验证，不能视为通过。")

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


def _last_line(text: str) -> str:
    lines = text.strip().splitlines()
    return lines[-1] if lines else ""


class RecordingResult(unittest.TextTestResult):
    """在 TextTestResult 基础上按用例记录 pass/fail/error/skip。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records: dict[str, CaseResult] = {}

    def _record(self, test, outcome: str, message: str = "") -> None:
        self.records[str(test)] = CaseResult(str(test), outcome, message)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, PASS)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, FAIL, _last_line(self.failures[-1][1]))

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, ERROR, _last_line(self.errors[-1][1]))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, SKIP, reason)

    def to_cases(self, expected_names: list[str]) -> list[CaseResult]:
        """按发现顺序输出用例结果。

        没有留下记录的用例（所属类 setUpClass 报错或被跳过，导致用例根本没执行）记为 skip；
        setUpClass 自身的报错会作为独立的 error 记录附在末尾，所以不会被漏算成通过。
        """
        cases = [
            self.records.get(name)
            or CaseResult(name, SKIP, "未执行（所属类 setUpClass 出错或被跳过）")
            for name in expected_names
        ]
        cases.extend(r for n, r in self.records.items() if n not in set(expected_names))
        return cases
