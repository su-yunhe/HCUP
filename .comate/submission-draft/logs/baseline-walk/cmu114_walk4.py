"""基线走查第四轮（临时脚本）：hint 是否被 BY.text 命中；router 压栈后底层页面节点是否还在 UI 树中。"""
from hypium import BY, UiDriver, MatchPattern

SN = "127.0.0.1:5555"
BUNDLE = "cc.chenlvin.cloudmusic"
d = UiDriver.connect(device_sn=SN)
d.stop_app(BUNDLE); d.start_app(BUNDLE); d.wait(3)
print("BY.text('请输入搜索词') on home:", d.find_component(BY.text("请输入搜索词")) is not None)
top = sorted(d.find_all_components(BY.type("Button")), key=lambda b: (b.getBounds().top, -b.getBounds().left))
d.click(top[0]); d.wait(1)
d.click(d.find_component(BY.text("下载管理"))); d.wait(2)
print("on Downloads, '下载管理' present:", d.find_component(BY.text("下载管理")) is not None)
print("on Downloads, home '云音汇' present:", d.find_component(BY.text("云音汇")) is not None)
print("on Downloads, home TextInput present:", d.find_component(BY.type("TextInput")) is not None)
d.press_back(); d.wait(1.5)
print("after back, '云音汇' present:", d.find_component(BY.text("云音汇")) is not None)
d.stop_app(BUNDLE)
