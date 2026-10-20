"""Host-only instrumentation check; never imports Hypium or contacts a device."""
from __future__ import annotations

import base64
import http.client
import json
from pathlib import Path
import socket
import sys

from webdav_fixture import WebDavFixture


def main():
    evidence = Path(sys.argv[1]).resolve()
    server = WebDavFixture(evidence)
    port = server.port
    checks = []
    try:
        seq = server.mark("host_selfcheck_boundary")
        server.set_mode("stored")
        assert server.observed_since(seq) == [], "In-process control polluted network statistics"
        checks.append("in_process_control_zero_tcp_and_http")
        client = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        auth = "Basic " + base64.b64encode(f"{server.username}:{server.password}".encode()).decode()
        headers = {"Authorization": auth}
        target = server.base_path + server.remote_root + "/backup.json.enc"
        for method, path, body, expected in (
            ("OPTIONS", server.base_path + "/", None, 200),
            ("PATCH", server.base_path + "/", None, 501),
            ("PUT", target, b"opaque-selfcheck-bytes", 201),
            ("HEAD", target, None, 200),
            ("GET", target, None, 200),
        ):
            client.request(method, path, body=body, headers=headers)
            response = client.getresponse()
            payload = response.read()
            assert response.status == expected, (method, response.status, expected)
            if method == "GET":
                assert payload == b"opaque-selfcheck-bytes"
        client.close()
        events = server.observed_since(seq)
        assert len([e for e in events if e["event"] == "tcp_accept"]) == 1
        requests = [e for e in events if e["event"] == "http_request"]
        assert [e["method"] for e in requests] == ["OPTIONS", "PATCH", "PUT", "HEAD", "GET"]
        assert all(e["authorization_matches"] for e in requests)
        checks += ["tcp_accept_independent_of_http_count", "all_http_methods_recorded",
                   "correct_auth_boolean", "uploaded_ciphertext_roundtrip"]
        assert auth not in server.ledger.path.read_text(encoding="utf-8")
        checks.append("authorization_value_not_persisted")
    finally:
        server.close()
    probe = socket.socket()
    try:
        assert probe.connect_ex(("127.0.0.1", port)) != 0, "Owned listener stayed open after graceful shutdown"
    finally:
        probe.close()
    checks.append("owned_listener_gracefully_closed")
    result = {"scope": "host fixture instrumentation only; not app validation",
              "status": "pass", "checks": checks, "exit_code": 0, "port": port}
    (evidence / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
