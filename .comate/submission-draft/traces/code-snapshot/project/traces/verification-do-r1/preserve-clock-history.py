"""Archive the actual clock-fault test version using recorded SHA/patch history."""
import difflib
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
VERSIONS = BASE / "script-versions"
new_test = (VERSIONS / "run-r2/test_main_tabs.py").read_text(encoding="utf-8")
start = new_test.index('        if "root" not in trace["before"]:\n')
end = new_test.index('        variants, distances = shape_variants(samples)\n', start)
old_test = new_test[:start] + new_test[end:]
expected_test = "ead35f8a0b1fc4831bf0d016cc86bfa090b53488d2e88b93bf69e5c281ba82dc"
assert hashlib.sha256(old_test.encode()).hexdigest() == expected_test
new_helper = (VERSIONS / "run-r2/evidence.py").read_text(encoding="utf-8")
old_helper = new_helper.replace("device wall clock plus host arrival", "device uptime plus host arrival")
old_helper = old_helper.replace('"stamp=$(date +%s.%N); echo FRAME_START $i $stamp; "',
                                '"read stamp rest < /proc/uptime; echo FRAME_START $i $stamp; "')
old_helper = old_helper.replace('"stamp=$(date +%s.%N); echo FRAME_END $i $stamp $rc; "',
                                '"read stamp rest < /proc/uptime; echo FRAME_END $i $stamp $rc; "')
old_helper = old_helper.replace(r'(\d+) (\d+\.\d+)(?: (\d+))?', r'(\d+) ([\d.]+)(?: (\d+))?')
old_helper = old_helper.replace('"deviceWallTime":', '"deviceUptime":')
line = '        self.e.cmd("file", "recv", self.remote, str(self.path))\n'
old_helper = old_helper.replace(line, '')
point = '        # hdc implementations differ in whether recv(dir, existing_dir) nests the source basename.\n'
old_helper = old_helper.replace(point, line + point)
directory = VERSIONS / "run-r1"
directory.mkdir(exist_ok=True)
(directory / "test_main_tabs.py").write_text(old_test, encoding="utf-8", newline="")
(directory / "evidence.py").write_text(old_helper, encoding="utf-8", newline="")
metadata = {"test_main_tabs.py": hashlib.sha256(old_test.encode()).hexdigest(),
            "evidence.py": hashlib.sha256(old_helper.encode()).hexdigest(),
            "provenance": {"test": "Exact reconstruction matches pre-run SHA from logs/verification-do-offline-r1.log",
                           "helper": "Reversed the recorded clock/collection patch; no independent pre-run complete helper SHA was recorded after JPEG suffix adaptation. This reconstruction is marked as such, not falsely independently confirmed."}}
(directory / "sha256-and-provenance.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
diff = ''.join(difflib.unified_diff(old_helper.splitlines(True), new_helper.splitlines(True),
                                  fromfile="run-r1/evidence.py", tofile="run-r2/evidence.py"))
(VERSIONS / "run-r1-to-run-r2-clock.diff").write_text(diff, encoding="utf-8")
context = BASE / "run-r1/run-context.json"
data = json.loads(context.read_text())
data["testSourceSHA256"] = {k: metadata[k] for k in ("test_main_tabs.py", "evidence.py")}
data["testVersionProvenance"] = metadata["provenance"]
context.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metadata, ensure_ascii=False))
