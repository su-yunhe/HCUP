#!/bin/bash
# 临时探测脚本：截图 + dump 布局 + 提取可见文本/id/bounds（不在工程目录内）
HDC=/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc
S="-t 127.0.0.1:5555"
N="$1"
$HDC $S shell "uitest screenCap -p /data/local/tmp/$N.png; uitest dumpLayout -p /data/local/tmp/$N.json" >/dev/null
$HDC $S file recv /data/local/tmp/$N.png /tmp/cmu-probe/$N.png >/dev/null
$HDC $S file recv /data/local/tmp/$N.json /tmp/cmu-probe/$N.json >/dev/null
/usr/bin/python3 - "$N" <<'EOF'
import json, sys
n = sys.argv[1]
d = json.load(open(f"/tmp/cmu-probe/{n}.json"))
def walk(node, depth=0):
    a = node.get("attributes", {})
    t = a.get("text", "")
    i = a.get("id", "") or a.get("key", "")
    typ = a.get("type", "")
    if t or i or typ in ("TextInput", "Button", "Toggle", "TextArea", "Search", "Select", "Radio"):
        print(f"{typ:14} id={i!r:20} text={t!r:40} bounds={a.get('bounds','')} clickable={a.get('clickable','')}")
    for c in node.get("children", []):
        walk(c, depth + 1)
walk(d)
EOF
