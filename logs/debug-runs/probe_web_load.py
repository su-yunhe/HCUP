from hypium import BY, UiDriver
d = UiDriver.connect(device_sn="127.0.0.1:5555")
B = "cc.chenlvin.cloudmusic"
bs = lambda: sorted(d.find_all_components(BY.type("Button")) or [], key=lambda b: (b.getBounds().top, b.getBounds().left))
d.stop_app(B); d.start_app(B, wait_time=3)
d.click(bs()[1]); d.wait(1); d.click(BY.text("设置")); d.wait(2)
d.click(BY.text("前往查看本软件的隐私政策")); d.wait(8)
d.press_back(); d.wait(1); d.stop_app(B)
