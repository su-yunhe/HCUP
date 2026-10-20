"""Check test syntax and the observer itself without loading Harness or touching a device."""
from __future__ import annotations

import ast
import http.client
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["VG_SPEC8_LOG_DIR"] = str(ROOT / "logs/implementation-validation/preparation-offline")
os.environ.pop("VG_SPEC8_RELEASED", None)

from hypium_tests.verification_support import LOG, MockDav, assert_release, hash_evidence, write_json


def main():
    files = sorted((ROOT / "hypium_tests").glob("*.py"))
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    try:
        assert_release()
        raise AssertionError("Missing release guard")
    except RuntimeError as error:
        assert "尚未释放" in str(error), str(error)
    mock = MockDav(port=0)
    mock.start()
    expected = ["HEAD", "GET", "PUT", "DELETE", "PROPFIND", "MKCOL", "OPTIONS", "POST", "TRACE", "PATCH", "FROB"]
    try:
        for method in expected:
            connection = http.client.HTTPConnection("127.0.0.1", mock.server.server_port, timeout=5)
            connection.request(method, "/dav/test-file.json", body=b"fixture" if method == "PUT" else None)
            response = connection.getresponse()
            response.read()
            connection.close()
        assert [item["method"] for item in mock.events] == expected
        assert mock.count() == len(expected)
        mock.checkpoint("offline-observer-all-methods", 0, purpose="test-tool-only; no-product-result")
    finally:
        mock.stop()
    result = {"syntaxFiles": [path.relative_to(ROOT).as_posix() for path in files],
              "releaseGuard": "pass", "realHttpMethodsObserved": expected, "exitCode": 0,
              "deviceTouched": False, "productRequirements": "all not_run"}
    write_json("offline-check-result.json", result)
    hash_evidence()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
