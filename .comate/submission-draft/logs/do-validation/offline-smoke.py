"""No device access: syntax/discovery and controlled fixture self-check."""
import ast
import json
import os
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hypium_tests.webdav_fixture import WebDavFixture

for source in sorted((ROOT / "hypium_tests").glob("*.py")):
    ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    print("SYNTAX_OK", source.name)

from harness.runner import discover, _collect_case_names
cases = _collect_case_names(discover(ROOT))
assert len(cases) == 11, cases
print("OFFLINE_DISCOVERY", json.dumps(cases))

fixture = WebDavFixture(ROOT / "logs/do-validation/offline-fixture", port=0)
base = f"http://127.0.0.1:{fixture.port}/smoke"
result = []

def put():
    request = urllib.request.Request(base, data=b"synthetic", method="PUT")
    with urllib.request.urlopen(request, timeout=5) as response:
        result.append(response.status)

try:
    worker = threading.Thread(target=put)
    worker.start()
    first = fixture.wait_request(0, timeout=3)
    assert not result and first["bodyBytes"] == 9
    fixture.release(first["id"])
    worker.join(timeout=3)
    assert result == [201], result
    fixture.configure(gated=False)
    with urllib.request.urlopen(base, timeout=3) as response:
        assert response.read() == b"synthetic"
    after = fixture.configure(gated=False, status=500)
    try:
        urllib.request.urlopen(base, timeout=3)
        raise AssertionError("Expected controlled 500")
    except urllib.error.HTTPError as error:
        assert error.code == 500
    assert fixture.requests(after)
    raw = fixture.log_path.read_text(encoding="utf-8")
    assert "synthetic" not in raw
    print("FIXTURE_OK gated PUT, stored GET, controlled 500, no payload logging")
finally:
    fixture.close()
print("OFFLINE_SMOKE_PASS; device features NOT_RUN")
