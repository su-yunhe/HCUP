from hypium import BY, UiDriver
d = UiDriver.connect(device_sn="127.0.0.1:5555")
B = "cc.chenlvin.cloudmusic"
def btns():
    bs = d.find_all_components(BY.type("Button")) or []
    return sorted(bs, key=lambda b: (b.getBounds().top, b.getBounds().left))
d.stop_app(B); d.start_app(B, wait_time=3)
d.click(btns()[1]); d.wait(1)
d.click(BY.text("设置")); d.wait(2)
for delay in [0, 0, 0, 1, 1, 1]:
    d.click(BY.text("前往查看本软件的隐私政策"))
    d.wait_for_component(BY.type("Web"), timeout=5)
    d.wait(delay)
    d.press_back(); d.wait(2)
    s = d.find_component(BY.text("当前版本")) is not None
    print(delay, "privacy back -> settings", s, "web", d.find_component(BY.type("Web")) is not None)
    if not s:
        d.press_back(); d.wait(2)
d.stop_app(B)
