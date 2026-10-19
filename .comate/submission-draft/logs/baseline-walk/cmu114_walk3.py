"""基线走查第三轮（临时脚本，跑完删除）：纯空格搜索落点、Web 组件在 UI 树中的类型。"""
import json, subprocess
from hypium import BY, UiDriver

SN = "127.0.0.1:5555"
BUNDLE = "cc.chenlvin.cloudmusic"
OUT = "/tmp/cmu114_walk"
d = UiDriver.connect(device_sn=SN)


def types(tag):
    subprocess.run(["hdc", "-t", SN, "shell", "uitest dumpLayout -p /data/local/tmp/l.json"], capture_output=True)
    subprocess.run(["hdc", "-t", SN, "file", "recv", "/data/local/tmp/l.json", f"{OUT}/{tag}.json"], capture_output=True)
    acc = []
    def walk(n):
        a = n.get("attributes", {})
        if a.get("bundleName", BUNDLE) == BUNDLE and a.get("type") in ("Web", "LoadingProgress", "Text", "TextInput", "Button"):
            acc.append((a.get("type"), a.get("text"), a.get("bounds")))
        for c in n.get("children", []):
            walk(c)
    walk(json.load(open(f"{OUT}/{tag}.json")))
    print(f"===== {tag} current_app={d.current_app()}")
    for x in acc:
        if x[1] not in ("01", "02", "03", "32", "33", "34", "35", ":", "100"):
            print("   ", x)
    d.capture_screen(f"{OUT}/{tag}.jpeg")


d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
inp = d.find_component(BY.type("TextInput"))
ib = inp.getBounds()
btn = [b for b in d.find_all_components(BY.type("Button"))
       if b.getBounds().left > ib.right and b.getBounds().top >= ib.top - 5][0]
print("search btn", btn.getBounds())
d.input_text(inp, "   ")
d.start_listen_toast()
d.click(btn)
print("toast(spaces):", repr(d.get_latest_toast(timeout=3)))
d.wait(5)
types("21_space_search_page")
d.press_back(); d.wait(1.5)
types("22_back_from_space_search")

# Web 组件：首页左上角 -> 登 录 -> 网页登录
d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
top = sorted(d.find_all_components(BY.type("Button")), key=lambda b: (b.getBounds().top, b.getBounds().left))
d.click(top[0]); d.wait(1.5)
d.click(d.find_component(BY.text("登 录"))); d.wait(2)
d.click(d.find_component(BY.text("网页登录"))); d.wait(4)
types("23_weblogin")
print("BY.type('Web') found:", d.find_component(BY.type("Web")) is not None)
d.press_back(); d.wait(2)
types("24_after_back_from_weblogin")
d.stop_app(BUNDLE)
