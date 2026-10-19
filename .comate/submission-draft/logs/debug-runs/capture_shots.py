from hypium import BY, UiDriver
d = UiDriver.connect(device_sn="127.0.0.1:5555")
B = "cc.chenlvin.cloudmusic"
def btns():
    bs = d.find_all_components(BY.type("Button")) or []
    return sorted(bs, key=lambda b: (b.getBounds().top, b.getBounds().left))
d.stop_app(B); d.start_app(B, wait_time=3)
d.capture_screen("shots/01_home_hint.jpeg")
d.input_text(BY.key("search_input"), "周杰伦"); d.wait(1)
d.capture_screen("shots/02_home_input_color.jpeg")
d.stop_app(B); d.start_app(B, wait_time=3)
d.click(btns()[1]); d.wait(1); d.click(BY.text("设置")); d.wait(2)
d.capture_screen("shots/03_settings.jpeg")
d.click(BY.text("前往查看本软件的隐私政策")); d.wait(0.8)
d.capture_screen("shots/04_privacy_immediate.jpeg")
d.wait(10)
d.capture_screen("shots/05_privacy_after_10s.jpeg")
print("texts on privacy page:", [t.getText() for t in (d.find_all_components(BY.type("Text")) or [])][:20])
d.press_back(); d.wait(2)
d.capture_screen("shots/06_back_settings.jpeg")
d.stop_app(B)
