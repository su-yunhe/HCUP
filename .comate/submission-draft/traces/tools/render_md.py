#!/usr/bin/env python3
"""Render a Comate native chat_session_<uuid> file into a readable Markdown copy.

Usage: render_md.py <chat_session_file> <blob_dir> <out.md> [max_chars]

- Resolves {"$blob": "sha256:..."} references from <blob_dir> (utf8 text or json;
  base64 image payloads are replaced by a placeholder in the Markdown only).
- Long tool params/results are cut at max_chars (default 4000) and marked
  "[truncated N of M chars]"; the untruncated data stays in the native files.
- Nothing is dropped otherwise: user messages, REASON, TOOL (incl. failed /
  skipped), TEXT are all emitted in original order.
"""
import datetime
import gzip
import json
import os
import sys

TZ = datetime.timezone(datetime.timedelta(hours=8))


def ts(ms):
    if not ms:
        return "-"
    return datetime.datetime.fromtimestamp(ms / 1000, TZ).strftime("%Y-%m-%d %H:%M:%S")


def load_blob(ref, blob_dir):
    sha = ref["$blob"].split(":", 1)[1]
    path = os.path.join(blob_dir, sha)
    if not os.path.exists(path):
        return "[blob missing: %s]" % sha
    raw = open(path, "rb").read()
    if ref.get("compression") == "gzip":
        raw = gzip.decompress(raw)
    text = raw.decode("utf8", errors="replace")
    if ref.get("encoding") == "json":
        try:
            return strip_images(json.loads(text), sha)
        except ValueError:
            return text
    return text


def strip_images(o, sha):
    """Replace base64 image payloads (screenshots) with a placeholder in the Markdown copy."""
    if isinstance(o, dict):
        if o.get("type") == "image" and isinstance(o.get("source"), dict) and "data" in o["source"]:
            src = dict(o["source"])
            src["data"] = "[base64 omitted in Markdown: %d chars, see native blob %s]" % (len(src["data"]), sha)
            return dict(o, source=src)
        return {k: strip_images(v, sha) for k, v in o.items()}
    if isinstance(o, list):
        return [strip_images(v, sha) for v in o]
    return o


def resolve(o, blob_dir):
    if isinstance(o, dict):
        if "$blob" in o:
            return load_blob(o, blob_dir)
        return {k: resolve(v, blob_dir) for k, v in o.items()}
    if isinstance(o, list):
        return [resolve(v, blob_dir) for v in o]
    return o


def clip(s, n):
    if len(s) <= n:
        return s
    return s[:n] + "\n...[truncated %d of %d chars]" % (n, len(s))


def fence(s):
    f = "```"
    while f in s:
        f += "`"
    return f


def block(s, n):
    s = clip(s, n)
    f = fence(s)
    return "%s\n%s\n%s\n" % (f, s, f)


def dump(o, n):
    if isinstance(o, str):
        return block(o, n)
    return block(json.dumps(o, ensure_ascii=False, indent=1), n)


def render_elem(e, blob_dir, n, out):
    t = e.get("type")
    if t == "REASON":
        out.append("**[REASON]** (%s)\n\n%s\n" % (ts(e.get("startTime")), e.get("content", "")))
    elif t == "TEXT":
        out.append("**[TEXT]**\n\n%s\n" % e.get("content", ""))
    elif t == "TOOL":
        params = resolve(e.get("params"), blob_dir)
        result = resolve(e.get("result"), blob_dir)
        out.append("**[TOOL] %s** state=`%s` id=`%s`\n" % (e.get("toolName"), e.get("toolState"), e.get("id")))
        out.append("params:\n" + dump(params, n))
        if isinstance(result, dict) and "output" in result:
            out.append("result.output:\n" + dump(result["output"], n))
            meta = {k: v for k, v in result.items() if k != "output"}
            if meta:
                out.append("result.metadata:\n" + dump(meta, 1500))
        else:
            out.append("result:\n" + dump(result, n))
    for c in e.get("children", []) or []:
        render_elem(c, blob_dir, n, out)


def main():
    src, blob_dir, dst = sys.argv[1:4]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
    d = json.load(open(src, encoding="utf-8"))
    out = ["# Session %s\n" % d["sessionUuid"]]
    out.append("- title: %s\n- workspace: %s\n- created: %s (UTC+8)\n- last updated: %s (UTC+8)\n- effort: %s\n- state when exported: see index\n"
               % (d.get("title"), d.get("workspaceDirectory"), ts(d.get("ctime")), ts(d.get("utime")), d.get("effort")))
    out.append("> Generated from the native session file by traces/tools/render_md.py (not the IDE sidebar export). Long tool params/results are truncated; the full data is in native/.\n")
    for m in d["messages"]:
        if m["role"] == "user":
            p = m.get("payload") or {}
            mdl = (p.get("model") or {}).get("displayName")
            out.append("\n---\n\n## USER %s  (%s)  model=%s\n" % (m["id"], ts(m.get("requestedAt")), mdl))
            c = m.get("content")
            out.append(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False))
            out.append("")
        else:
            out.append("\n---\n\n## ASSISTANT %s  (completed %s)  status=%s\n" % (m["id"], ts(m.get("completedAt")), m.get("status")))
            out.append("tokenUsage=%s  performanceMetrics=%s\n" % (json.dumps(m.get("tokenUsage")), json.dumps(m.get("performanceMetrics"))))
            for e in m.get("elements", []) or []:
                render_elem(e, blob_dir, n, out)
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
