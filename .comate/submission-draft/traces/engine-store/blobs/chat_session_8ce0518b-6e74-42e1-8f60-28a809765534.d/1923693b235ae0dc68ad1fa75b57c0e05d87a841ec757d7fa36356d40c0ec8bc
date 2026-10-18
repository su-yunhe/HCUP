"""生成"查看原文"自测数据（场景四）。

官方名句数据集的 poem_id 全为 null，无法覆盖"查看原文"正向用例。本脚本基于官方数据集生成一份
只含部分名句的导入文件，经 设置→导入数据→诗文名句 导入后按 id 覆盖（ON_CONFLICT_REPLACE）：

- 出处"作者《标题》"能唯一匹配诗词 writer+title 的名句：poem_id = 该诗词 id（有关联，应显示入口）
- 另取若干未匹配名句：poem_id = 99999（指向不存在的诗词，不应显示入口）
- 另取若干未匹配名句：poem_id = 0（视为无关联，不应显示入口）

用法：
    python3 make_fixture.py <官方名句 JSON> <官方诗词 JSON> <输出 JSON>
输出文件按导入格式 {"total","data","next_page"} 写出；测试用例读取同一文件判断每条名句的期望。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict

MISSING_POEM_ID = 99999
MISSING_COUNT = 800
ZERO_COUNT = 200
FROM_PATTERN = re.compile(r"^(.+)《(.+)》$")


def build(sentences: list[dict], poems: list[dict]) -> list[dict]:
    by_writer_title: dict[tuple[str, str], list[int]] = defaultdict(list)
    for poem in poems:
        by_writer_title[(poem["writer"], poem["title"])].append(poem["id"])

    linked, unlinked = [], []
    for s in sentences:
        m = FROM_PATTERN.match(s["from"])
        ids = by_writer_title.get((m.group(1), m.group(2)), []) if m else []
        if len(ids) == 1:
            linked.append({**s, "poem_id": ids[0]})
        else:
            unlinked.append(s)

    missing = [{**s, "poem_id": MISSING_POEM_ID} for s in unlinked[:MISSING_COUNT]]
    zero = [{**s, "poem_id": 0} for s in unlinked[MISSING_COUNT:MISSING_COUNT + ZERO_COUNT]]
    return linked + missing + zero


def main(argv: list[str]) -> None:
    sentence_path, poem_path, out_path = argv
    sentences = json.load(open(sentence_path, encoding="utf-8"))["data"]
    poems = json.load(open(poem_path, encoding="utf-8"))["data"]
    data = build(sentences, poems)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(data), "data": data, "next_page": None}, f, ensure_ascii=False)
    linked = sum(1 for d in data if d["poem_id"] not in (0, MISSING_POEM_ID))
    print(f"written {len(data)} sentences ({linked} linked) to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
