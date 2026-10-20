"""Host-only fixture protocol check; does not prove application acceptance."""
import http.client
import json
from pathlib import Path
import sys
import base64

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hypium_tests.webdav_fixture import WebDavFixture

output = ROOT / "traces/implementation-validation/preparation/fixture-selfcheck"
fixture = WebDavFixture(output, port=0)
fixture.start()
checks = []
auth = "Basic " + base64.b64encode(f"{fixture.USER}:{fixture.PASSWORD}".encode()).decode()


def request(method, path, body=None, authenticated=True):
    connection = http.client.HTTPConnection("127.0.0.1", fixture.port, timeout=10)
    connection.request(method, path, body=body, headers={"Authorization": auth} if authenticated else {})
    response = connection.getresponse()
    status, payload, location = response.status, response.read(), response.getheader("Location")
    connection.close()
    return status, payload, location


try:
    scenario = fixture.create("selfcheck", gate_first=False, delay=0)
    assert request("HEAD", scenario.root, authenticated=False)[0] == 401
    assert request("HEAD", scenario.root)[0] == 200
    assert request("GET", scenario.root + "/data")[0] == 404
    assert request("PUT", scenario.root + "/data", b"synthetic-stored-bytes")[0] == 201
    assert request("GET", scenario.root + "/data")[:2] == (200, b"synthetic-stored-bytes")
    assert request("DELETE", scenario.root + "/data")[0] == 204
    checks.append("auth/head/missing/put/get/delete")
    forbidden = fixture.create("forbidden", mode="forbidden", gate_first=False, delay=0)
    assert request("GET", forbidden.root)[0] == 403
    checks.append("received-http403")
    redirect = fixture.create("redirect", gate_first=False, delay=0.01, redirect_hops=2)
    path = redirect.root
    for expected_status in (307, 307, 200):
        status, _, location = request("HEAD", path)
        assert status == expected_status, status
        if location:
            path = location
    checks.append("two-real307-hops")
    tree = fixture.create("tree", root="/vg-spec9-selfcheck-tree/a/b", mode="long_tree", gate_first=False, delay=0)
    assert request("HEAD", tree.root)[0] == 404
    for collection in ("/vg-spec9-selfcheck-tree", "/vg-spec9-selfcheck-tree/a", tree.root):
        assert request("HEAD", collection)[0] == 404
        assert request("PUT", collection + "/.keep", b"keep")[0] == 201
        assert request("HEAD", collection)[0] == 200
    assert request("GET", tree.root + "/words_delta.jsonl.enc")[0] == 404
    checks.append("real-nested-directory-creation-head-put-recheck")
    print(json.dumps({"result": "pass", "scope": "host fixture only", "checks": checks}))
finally:
    fixture.close()
