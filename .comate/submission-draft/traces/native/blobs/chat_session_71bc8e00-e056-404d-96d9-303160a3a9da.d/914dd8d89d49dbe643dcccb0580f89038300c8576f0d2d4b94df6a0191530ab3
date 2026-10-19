"""基线走查第二轮（临时脚本，跑完删除）：前台应用、Web 组件在 UI 树中的类型、纯空格搜索、返回行为。"""
import json, subprocess
from hypium import BY, UiDriver, MatchPattern

SN = "127.0.0.1:5555"
BUNDLE = "cc.chenlvin.cloudmusic"
OUT = "/tmp/cmu114_walk"
d = UiDriver.connect(device_sn=SN)
SKIP = ("Status", "status_", "Battery", "Wifi", "Signal", "TimeView", "sbg_", "Live", "session", "Clock", "keyboard", "Key", "downMenu", "index_", "Skin", "parentLayout", "inputMethod", "kbd_")


def dump(tag):
    subprocess.run(["hdc", "-t", SN, "shell", "uitest dumpLayout -p /data/local/tmp/l.json"], capture_output=True)
    subprocess.run(["hdc", "-t", SN, "file", "recv", "/data/local/tmp/l.json", f"{OUT}/{tag}.json"], capture_output=True)
    print(f"===== {tag}  current_app={d.current_app()}")
    def walk(n):
        a = n.get("attributes", {})
        i = a.get("id") or ""
        if not any(s in i for s in SKIP) and a.get("type") not in ("Column", "Row", "Stack", "__Common__", "Flex", "RelativeContainer", "SymbolGlyph", "root", "ListItem"):
            print("   ", a.get("type"), repr(i), repr(a.get("text")), repr(a.get("hint")), a.get("bounds"))
        for c in n.get("children", []):
            walk(c)
    walk(json.load(open(f"{OUT}/{tag}.json")))


d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
print("home current_app:", d.current_app())

# 纯空格搜索：观察进入的页面
inp = d.find_component(BY.type("TextInput"))
d.input_text(inp, "   ")
btn = [b for b in d.find_all_components(BY.type("Button")) if b.getBounds().left > inp.getBounds().right and b.getBounds().top < 500][0]
d.click(btn); d.wait(4)
dump("11_space_search_page")
d.press_back(); d.wait(1)
d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)

# 设置页文本匹配方式
top = sorted(d.find_all_components(BY.type("Button")), key=lambda b: (b.getBounds().top, -b.getBounds().left))
d.click(top[0]); d.wait(1)
d.click(d.find_component(BY.text("设置"))); d.wait(2)
print("EQUALS '云音汇 @Chenlvin':", d.find_component(BY.text("云音汇 @Chenlvin")) is not None)
print("CONTAINS '云音汇 @Chenlvin':", d.find_component(BY.text("云音汇 @Chenlvin", MatchPattern.CONTAINS)) is not None)
print("CONTAINS 'CloudMusic-HarmonyOSNext':", d.find_component(BY.text("CloudMusic-HarmonyOSNext", MatchPattern.CONTAINS)) is not None)
print("EQUALS '0.9.2 - 测试版':", d.find_component(BY.text("0.9.2 - 测试版")) is not None)
print("count '隐私政策' EQUALS:", len(d.find_all_components(BY.text("隐私政策")) or []))

# 隐私政策：外部浏览器
d.click(d.find_component(BY.text("前往查看本软件的隐私政策"))); d.wait(3)
print("after privacy click current_app:", d.current_app())
print("Web type present:", d.find_component(BY.type("Web")) is not None)
d.press_back(); d.wait(2)
print("after 1x back current_app:", d.current_app())
d.press_back(); d.wait(2)
print("after 2x back current_app:", d.current_app())
dump("12_after_2x_back")

# Web 组件在 UI 树中的呈现：首页左上角 -> 半模态 -> 登录 -> 网页登录
d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
top = sorted(d.find_all_components(BY.type("Button")), key=lambda b: (b.getBounds().top, b.getBounds().left))
d.click(top[0]); d.wait(1.5)
dump("13_me_sheet")
