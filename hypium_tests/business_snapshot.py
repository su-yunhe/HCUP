"""Read-only on-device SQLite snapshot; inspect copies inside evidence only."""
import base64
import hashlib
import json
from pathlib import Path
import sqlite3


def logical_snapshot(evidence, label: str, remote_directory: str) -> dict:
    destination = evidence.root / label
    destination.mkdir(parents=True, exist_ok=True)
    listing = evidence.hdc("shell", f"ls -1 {remote_directory}")
    filenames = [name.strip() for name in listing.stdout.splitlines()
                 if name.strip().startswith("vignette.db") and "/" not in name.strip()]
    if "vignette.db" not in filenames:
        raise RuntimeError("Cannot capture the app business database; see raw bundle-scoped ls log")
    fingerprints = {}
    for name in filenames:
        target = destination / name
        evidence.hdc("file", "recv", remote_directory + "/" + name, str(target))
        if not target.is_file():
            raise RuntimeError("hdc did not actually copy business database artifact: " + name)
        fingerprints[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    database = destination / "vignette.db"
    connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    tables = {}
    try:
        names = connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        for (name,) in names:
            if name.startswith("sqlite_"):
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            cursor = connection.execute("SELECT * FROM " + quoted)
            columns = [item[0] for item in cursor.description]
            rows = []
            for row in cursor:
                values = [({"blob_base64": base64.b64encode(value).decode()} if isinstance(value, bytes) else value)
                          for value in row]
                rows.append(json.dumps(values, ensure_ascii=False, separators=(",", ":")))
            rows.sort()
            serialized = json.dumps({"columns": columns, "rows": rows}, ensure_ascii=False, separators=(",", ":"))
            tables[name] = {"rows": len(rows), "columns": columns,
                            "logical_sha256": hashlib.sha256(serialized.encode()).hexdigest()}
    finally:
        connection.close()
    result = {"label": label, "scope": "all non-sqlite-internal tables in current app vignette.db",
              "method": "device file recv only; SQLite SELECT on local copies; no device SQL or writes",
              "remote_directory": remote_directory, "copied_file_sha256": fingerprints, "tables": tables}
    evidence.write(label + "-logical.json", result)
    return tables
