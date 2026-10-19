"""基线走查第五轮（临时脚本）：hint 选择器、文本唯一性、两种返回路径、快速连点、重启后重进。"""
from hypium import BY, UiDriver, MatchPattern

SN = "127.0.0.1:5555"
BUNDLE = "cc.chenlvin.cloudmusic"
d = UiDriver.connect(device_sn=SN)


def cnt(by):
    return len(d.find_all_components(by) or [])


def top_buttons():
    # 首页顶栏：左=菜单(半模态)，右=更多；搜索按钮在第二行
    bs = d.find_all_components(BY.type("Button")) or []
    return sorted(bs, key=lambda b: (b.getBounds().top, b.getBounds().left))


def open_settings():
    bs = top_buttons()
    d.click(bs[1]); d.wait(1)
    d.click(d.find_component(BY.text("设置"))); d.wait(2)


d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
print("[home] BY.hint('请输入搜索词'):", d.find_component(BY.hint("请输入搜索词")) is not None)
ti = d.find_component(BY.type("TextInput"))
print("[home] TextInput.getHint():", repr(ti.getHint()), "getText():", repr(ti.getText()))
props = ti.getAllProperties()
print("[home] TextInput props keys:", sorted(list(props.keys())) if hasattr(props, "keys") else props)
print("[home] count text '云音汇':", cnt(BY.text("云音汇")))

# 空搜索：快速连点两次
search_btn = top_buttons()[2]
d.start_listen_toast()
d.click(search_btn); d.click(search_btn)
print("[home] toast after 2x fast click:", repr(d.get_latest_toast(timeout=3)))
d.wait(1)
print("[home] after empty click current_app:", d.current_app(), "'云音汇' present:",
      d.find_component(BY.text("云音汇")) is not None,
      "LoadingProgress present:", d.find_component(BY.type("LoadingProgress")) is not None)

# 设置页文本唯一性
open_settings()
for t in ["设置", "当前版本", "0.9.2 - 测试版", "隐私政策", "问题反馈", "前往查看本软件的隐私政策"]:
    print(f"[settings] count EQUALS '{t}':", cnt(BY.text(t)))
print("[settings] count CONTAINS '云音汇':", cnt(BY.text("云音汇", MatchPattern.CONTAINS)))
print("[settings] home TextInput present:", d.find_component(BY.type("TextInput")) is not None)

# 返回路径 1：系统返回
d.press_back(); d.wait(1.5)
print("[back#1 press_back] '云音汇' present:", d.find_component(BY.text("云音汇")) is not None,
      "hint present:", d.find_component(BY.hint("请输入搜索词")) is not None)

# 返回路径 2：页面左上返回按钮
open_settings()
d.click(top_buttons()[0]); d.wait(1.5)
print("[back#2 BackButton] '云音汇' present:", d.find_component(BY.text("云音汇")) is not None,
      "'当前版本' present:", d.find_component(BY.text("当前版本")) is not None)

# 重启后重进
d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
print("[restart] hint present:", d.find_component(BY.hint("请输入搜索词")) is not None)
open_settings()
print("[restart] version text:", d.find_component(BY.text("0.9.2 - 测试版")) is not None)
d.stop_app(BUNDLE)
