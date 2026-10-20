"""Independently authenticate/decrypt only this round's synthetic-fixture uploads.

Matches the task's WebDavCrypto v1 PBKDF2-SHA256/10000/AES256CTR/HMAC.
Reports schema and collection sizes, not users' word contents.
"""
import base64
import hashlib
import hmac
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
from hypium_tests.webdav_fixture import WebDavFixture

out = root / "traces/implementation-validation" / sys.argv[1]
rows = []
for file in sorted(out.glob("put-*.bin")):
    raw = file.read_bytes()
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        continue  # Directory .keep/probe bodies are not encrypted business uploads.
    if not isinstance(payload, dict) or payload.get("v") != 1 or "ct" not in payload:
        continue
    salt, iv, ciphertext, mac = [base64.b64decode(payload[key]) for key in ("salt", "iv", "ct", "mac")]
    derived = hashlib.pbkdf2_hmac("sha256", WebDavFixture.SYNC_PASSWORD.encode(), salt, 10000, 64)
    expected = hmac.new(derived[32:], salt + iv + ciphertext, hashlib.sha256).digest()
    assert hmac.compare_digest(mac, expected), f"Fixture upload MAC mismatch: {file.name}"
    decryptor = Cipher(algorithms.AES(derived[:32]), modes.CTR(iv)).decryptor()
    plain = (decryptor.update(ciphertext) + decryptor.finalize()).decode("utf-8")
    records = []
    for line in plain.splitlines():
        item = json.loads(line)
        if isinstance(item, dict):
            records.append({"keys": sorted(item),
                            "array_lengths": {key: len(value) for key, value in item.items() if isinstance(value, list)},
                            "count_fields": {key: value for key, value in item.items()
                                             if isinstance(value, (int, float)) and ("count" in key.lower() or "total" in key.lower())}})
        else:
            records.append({"json_type": type(item).__name__})
    rows.append({"file": file.name, "body_sha256": hashlib.sha256(raw).hexdigest(),
                 "mac_valid": True, "plaintext_bytes": len(plain.encode()), "records": records})
(out / "business-upload-summary.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rows, ensure_ascii=False, indent=2))
