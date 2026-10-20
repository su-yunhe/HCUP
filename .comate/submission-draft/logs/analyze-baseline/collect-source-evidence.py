"""Read-only, line-numbered local baseline source excerpts."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
selections = {
    "entry/src/main/ets/pages/Index.ets": [(288, 310), (450, 482)],
    "entry/src/main/ets/pages/SettingsPage.ets": [(35, 50), (447, 462), (520, 535)],
    "entry/src/main/ets/pages/settings/SettingsSyncSection.ets": [(100, 123), (165, 286), (343, 398), (429, 443), (466, 471), (533, 624)],
    "entry/src/main/ets/sync/WebDavSyncManager.ets": [(164, 182), (284, 304), (475, 503)],
    "entry/src/main/ets/sync/webdav/WebDavBackupManager.ets": [(70, 129)],
    "entry/src/main/ets/sync/webdav/WebDavClient.ets": [(125, 149)],
}
output = []
for relative, ranges in selections.items():
    path = ROOT / relative
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    lines = text.splitlines()
    output.extend([f"FILE {relative}", f"SHA256 {hashlib.sha256(data).hexdigest()}"])
    if relative.endswith("SettingsSyncSection.ets"):
        output.append("FULL-FILE TOKEN SEARCH LoadingProgress: " + str(text.count("LoadingProgress")) + " matches")
        output.append("FULL-FILE TOKEN SEARCH .id(: " + str(text.count(".id(")) + " matches")
    for first, last in ranges:
        for index in range(first - 1, min(last, len(lines))):
            output.append(f"{relative}:{index+1}: {lines[index]}")
    output.append("")
(EVIDENCE / "source-observations.txt").write_text("\n".join(output), encoding="utf-8")
print("written source-observations.txt lines", len(output))
