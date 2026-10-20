"""Validate peer-close instrumentation independently of the device application."""
import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
from hypium_tests.webdav_fixture import WebDavFixture

fixture = WebDavFixture(root / "logs/do-validation/offline-timeout-fixture", port=0)
timeouts = []

def client():
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{fixture.port}/timeout", timeout=0.3)
    except TimeoutError:
        timeouts.append(True)

try:
    fixture.configure(gated=True, hold_seconds=3)
    thread = threading.Thread(target=client)
    thread.start()
    request = fixture.wait_request(0, timeout=2)
    thread.join(timeout=2)
    assert timeouts == [True]
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        closed = [r for r in fixture.records if r["event"] == "client_closed"]
        if closed:
            break
        time.sleep(0.1)
    assert closed, fixture.records
    assert not [r for r in fixture.records if r["event"] == "response"]
    print(json.dumps({"fixture_timeout_instrumentation": "pass", "peer_closed_before_server_response": True,
                      "elapsed_ms": (closed[0]["monotonic_ns"] - request["monotonic_ns"]) / 1_000_000}))
finally:
    fixture.close()
