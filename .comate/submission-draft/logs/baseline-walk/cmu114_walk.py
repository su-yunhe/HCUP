"""基线走查（临时脚本，跑完删除）。只读操作 UI，不改工程。"""
import json, subprocess, sys, time
from hypium import BY, UiDriver

SN = "127.0.0.1:5555"
BUNDLE = "cc.chenlvin.cloudmusic"
OUT = "/tmp/cmu114_walk"
subprocess.run(["mkdir", "-p", OUT])
d = UiDriver.connect(device_sn=SN)


def hdc(cmd):
    return subprocess.run(["hdc", "-t", SN, "shell", cmd], capture_output=True, text=True).stdout


def dump(tag):
    out = hdc("uitest dumpLayout -p /data/local/tmp/l.json")
    subprocess.run(["hdc", "-t", SN, "file", "recv", "/data/local/tmp/l.json", f"{OUT}/{tag}.json"], capture_output=True)
    nodes = []
    def walk(n):
        a = n.get("attributes", {})
        if a.get("text") or a.get("hint") or a.get("id") or a.get("type") in ("TextInput", "Web", "Button", "Image", "MenuItem", "Search"):
            nodes.append((a.get("type"), a.get("id"), a.get("key"), a.get("text"), a.get("hint"), a.get("bounds"), a.get("clickable")))
        for c in n.get("children", []):
            walk(c)
    try:
        walk(json.load(open(f"{OUT}/{tag}.json")))
    except Exception as e:
        print("dump fail", e, out)
    print(f"===== {tag}")
    for x in nodes:
        print("  ", x)
    try:
        d.capture_screen(f"{OUT}/{tag}.jpeg")
    except Exception as e:
        print("shot fail", e)


def fg():
    r = hdc("aa dump -l")
    lines = [l.strip() for l in r.splitlines() if "bundle name" in l or "main name" in l or "state" in l.lower()]
    print("  foreground:", lines[:6])


step = sys.argv[1] if len(sys.argv) > 1 else "all"

d.stop_app(BUNDLE)
d.start_app(BUNDLE)
d.wait(3)
dump("01_home")
fg()

# 场景三：空输入点搜索
d.start_listen_toast()
btns = d.find_all_components(BY.type("Button")) or []
print("buttons:", [(b.getBounds()) for b in btns])
inp = d.find_component(BY.type("TextInput"))
ib = inp.getBounds()
# 搜索按钮：与输入框同一行、在其右侧的 Button
search_btn = [b for b in btns if b.getBounds().left > ib.right and abs((b.getBounds().top + b.getBounds().bottom) - (ib.top + ib.bottom)) < 80]
print("search btn:", [b.getBounds() for b in search_btn])
d.click(search_btn[0])
toast = d.get_latest_toast(timeout=3)
print("TOAST(empty):", repr(toast))
d.wait(1)
dump("02_after_empty_search")

# 纯空格
d.input_text(inp, "   ")
d.wait(0.5)
d.start_listen_toast()
d.click(search_btn[0])
toast = d.get_latest_toast(timeout=3)
print("TOAST(spaces):", repr(toast))
d.wait(2)
dump("03_after_space_search")
d.press_back()
d.wait(1)
dump("03b_after_back")

# 场景一：更多菜单 -> 设置
d.stop_app(BUNDLE)
d.start_app(BUNDLE)
d.wait(3)
btns = d.find_all_components(BY.type("Button")) or []
top = sorted(btns, key=lambda b: (b.getBounds().top, b.getBounds().left))
more = max([b for b in top if b.getBounds().top == top[0].getBounds().top], key=lambda b: b.getBounds().left)
print("more btn:", more.getBounds())
d.click(more)
d.wait(1)
dump("04_more_menu")
d.click(d.find_component(BY.text("设置")))
d.wait(2)
dump("05_settings")
fg()

# 场景二：点击隐私政策
d.click(d.find_component(BY.text("前往查看本软件的隐私政策")))
d.wait(3)
dump("06_after_privacy_click")
fg()
d.press_back()
d.wait(2)
dump("07_after_back")
fg()
