"""Independent live login controls assertions; absent expected controls fail explicitly."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
from hypium import UiDriver, BY

root = Path(__file__).resolve().parents[2]
driver = UiDriver.connect(device_sn="127.0.0.1:5555")
driver.set_implicit_wait_time(0.5)
rows = []
for requirement, text in [
    ("A1", "登录"), ("A6", "手机号登录"), ("A10", "账号密码登录"),
    ("B1", "其他登录方式"), ("B6", "微信"), ("B7", "QQ"),
    ("B8", "支付宝"), ("B12", "用户协议"), ("B13", "隐私政策")
]:
    component = driver.find_component(BY.text(text))
    try:
        assert component is not None, f"Expected visible login text absent: {text}"
        rows.append({"requirement": requirement, "text": text, "status": "pass", "bounds": str(component.getBounds())})
    except AssertionError as error:
        rows.append({"requirement": requirement, "text": text, "status": "fail", "error": str(error)})
result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "device": "127.0.0.1:5555",
          "note": "A1 navigation is independently backed by before/after action snapshots; title alone is insufficient.",
          "checks": rows}
target = root / "logs" / "analysis-baseline" / "login-assertions.json"
target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(1 if any(row["status"] == "fail" for row in rows) else 0)
