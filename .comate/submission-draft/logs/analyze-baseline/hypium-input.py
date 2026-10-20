"""Use documented component test input; do not accept system agreements."""
import sys
from pathlib import Path
import runpy
from hypium import BY, UiDriver
from hypium.model.basic_data_type import InputTextMode
evidence = runpy.run_path(str(Path(__file__).with_name("device-evidence.py")))
event, snapshot, run, summarize, ROOT = (evidence[name] for name in ("event", "snapshot", "run", "summarize", "ROOT"))

driver = UiDriver.connect(device_sn="127.0.0.1:5555")
driver.set_implicit_wait_time(1)
event("hypium_connected", device="127.0.0.1:5555")
fields = driver.find_all_components(BY.type("TextInput")) or []
event("hypium_fields", count=len(fields), operation=sys.argv[1:])
if len(sys.argv) > 1 and sys.argv[1] == "fill":
    index = int(sys.argv[2])
    value = sys.argv[3]
    name = sys.argv[4]
    driver.input_text(fields[index], value, mode=InputTextMode().paste(True))
    event("hypium_input", field_index=index, value=value, mode="paste(True)")
    snapshot(name)
    summarize(ROOT / (name + ".json"))
elif len(sys.argv) > 1 and sys.argv[1] == "fill_all":
    values = ["http://127.0.0.1:18085", "spec15-user", "BaselineOnly15!", "Spec15Sync!", "/baseline-spec15"]
    for index, value in enumerate(values):
        fields = driver.find_all_components(BY.type("TextInput")) or []
        if len(fields) != 5:
            raise RuntimeError(f"Expected five configuration fields, got {len(fields)}")
        driver.input_text(fields[index], value, mode=InputTextMode().paste(True))
        event("hypium_input", field_index=index, value=value, mode="paste(True), default replace")
        run(["shell", "uitest", "uiInput", "keyEvent", "Back"], f"hypium-dismiss-keyboard-{index}")
    snapshot("19-configuration-filled")
    summarize(ROOT / "19-configuration-filled.json")
