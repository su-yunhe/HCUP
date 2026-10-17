#!/usr/bin/env python3
"""Render a native Comate chat_session_<uuid> file into a readable Markdown copy.

Usage: render_session_md.py <native/chat_session_UUID> <out.md> [--max-chars N]

The native file is JSON; large strings are stored as {"$blob": "sha256:<hex>"}
references, resolved from native/blobs/chat_session_<uuid>.d/<hex>.
Long values are truncated in the Markdown copy only (the native files are untouched).
"""
import datetime
import json
import os
import sys

TZ = datetime.timezone(datetime.timedelta(hours=8))


def ts(ms):
    if not isinstance(ms, (int, float)):
        return str(ms)
    return datetime.datetime.fromtimestamp(ms / 1000, TZ).strftime("%Y-%m-%d %H:%M:%S+08:00")


def main():
    src, out = sys.argv[1], sys.argv[2]
    max_chars = 4000
    if "--max-chars" in sys.argv:
        max_chars = int(sys.argv[sys.argv.index("--max-chars") + 1])
    uuid = os.path.basename(src).replace("chat_session_", "")
    blob_dir = os.path.join(os.path.dirname(src), "blobs", f"chat_session_{uuid}.d")
    d = json.load(open(src, encoding="utf-8"))

    def clip(s):
        s = str(s)
        if len(s) <= max_chars:
            return s
        return s[:max_chars] + f"\n... [truncated in Markdown copy, {len(s)} chars total; see native file]"

    def resolve(o):
        if isinstance(o, dict):
            if "$blob" in o:
                h = o["$blob"].split(":", 1)[-1]
                p = os.path.join(blob_dir, h)
                if os.path.exists(p):
                    return open(p, "rb").read().decode("utf-8", "replace")
                return f"<blob {h} missing>"
            return {k: resolve(v) for k, v in o.items()}
        if isinstance(o, list):
            return [resolve(v) for v in o]
        return o

    def walk(els):
        for e in els or []:
            if isinstance(e, dict):
                if "children" in e:
                    yield from walk(e["children"])
                else:
                    yield e

    L = [f"# Comate 会话 Markdown 副本：{d.get('title','')}", ""]
    L += [f"- sessionUuid：`{d.get('sessionUuid')}`", f"- specSessionId（IDE 侧边栏会话 ID）：`{d.get('specSessionId')}`",
          f"- 创建：{ts(d.get('ctime'))}；最后更新：{ts(d.get('utime'))}", f"- effort：{d.get('effort')}",
          "- 说明：由 `render_session_md.py` 从 `native/chat_session_<uuid>` 生成的派生副本，不是 IDE「导出本地」产物；以 native 文件为准。", ""]
    for i, m in enumerate(d.get("messages", [])):
        if m.get("role") == "user":
            p = m.get("payload") or {}
            mdl = (p.get("model") or {})
            L += [f"## [{i}] 用户 · {ts(m.get('requestedAt'))} · {mdl.get('displayName')}/{mdl.get('effort')}", "", clip(resolve(m.get("content"))), ""]
        else:
            tu = m.get("tokenUsage") or {}
            L += [f"## [{i}] 助手 · 完成 {ts(m.get('completedAt'))} · status={m.get('status')} · contextUsed={tu.get('contextUsed')}", ""]
            for e in walk(m.get("elements")):
                t = e.get("type")
                if t == "REASON":
                    L += ["> 思考：" + clip(resolve(e.get("content"))).replace("\n", "\n> "), ""]
                elif t == "TEXT":
                    L += [clip(resolve(e.get("content"))), ""]
                elif t == "TOOL":
                    params = clip(json.dumps(resolve(e.get("params")), ensure_ascii=False, indent=1))
                    res = resolve((e.get("result") or {}).get("output"))
                    L += [f"**工具** `{e.get('toolName')}` · state=`{e.get('toolState')}`", "", "```json", params, "```", "", "结果：", "", "```", clip(res), "```", ""]
                else:
                    L += [f"(未识别元素类型 {t})", ""]
    open(out, "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    main()
