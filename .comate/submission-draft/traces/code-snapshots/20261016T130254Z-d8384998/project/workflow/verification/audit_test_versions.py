"""Record historical/current local test versions without changing production."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
base = root / "traces/implementation-validation"
current_fixture = (root / "hypium_tests/webdav_fixture.py").read_bytes()
new_gate = b"scenario.release.wait(timeout=min(16, max(0, 18 - scenario.delay)))"
old_gate = b"scenario.release.wait(timeout=16)"
assert current_fixture.count(new_gate) == 1
historical_fixture = current_fixture.replace(new_gate, old_gate)
for name in ("round02-t1-retry", "round02-regression"):
    (base / name / "fixture-source-used.py").write_bytes(historical_fixture)
manifest = {"historical_fixture": {"sha256": hashlib.sha256(historical_fixture).hexdigest(),
                                   "source": "fixture-source-used.py under the historical run folders",
                                   "reconstruction": "Exact prior fixture text reconstructed from the single recorded gate-limit edit; no runtime monkeypatch."},
            "current_fixture": {"sha256": hashlib.sha256(current_fixture).hexdigest(),
                                "change": "Gate timeout min(16, max(0,18-delay)); combined gate+delay <=18s."},
            "historical_test": {"sha256": hashlib.sha256((base / "round02-regression/test-source-used.py").read_bytes()).hexdigest()},
            "current_test": {"sha256": hashlib.sha256((root / "hypium_tests/test_webdav_loading.py").read_bytes()).hexdigest()}}
(base / "round02-test-versions.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False, indent=2))
