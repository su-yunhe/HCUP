#Requires -RunAsAdministrator
# vg-spec1 reviewed helper05; user launches this in an already elevated PowerShell.
# No automatic RunAs/UAC, policy changes, downloads or device lifecycle operations.
$ErrorActionPreference = 'Stop'
$root = 'D:/HCUP/vg-spec1'
$freeze = 'D:/HCUP/vg-spec1/logs/development-round-03/wfp-build/20261017-182636-9243f7/frozen-review-05-fingerprint.json'
if ((Get-FileHash -LiteralPath $freeze -Algorithm SHA256).Hash.ToLowerInvariant() -ne '8d126e6db7ede1a65f8c1d614ad1f21f9070790ec066039a1062cd1e925b52dd') {
    throw 'The reviewed helper source manifest changed. Do not launch.'
}
$reviewed = Get-Content -LiteralPath $freeze -Raw | ConvertFrom-Json
foreach ($source in $reviewed.sources) {
    if ((Get-FileHash -LiteralPath (Join-Path $root $source.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $source.sha256) {
        throw ('Reviewed helper source changed: ' + $source.path)
    }
}
$exe = 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/bin/VgSpec1WfpGuard.exe'
if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant() -ne '707a713899c97004d8e9df46d1b0c5fe012e0102b9024d7abf3b05bb590e694a') {
    throw 'The reviewed helper executable changed. Do not launch.'
}
$runtime = 'D:/HCUP/vg-spec1/logs/development-round-02/wfp-offline-round-01/wfp-runtime'
if (-not (Test-Path -LiteralPath $runtime -PathType Container)) { throw 'Test watcher is not prepared.' }
if (Test-Path -LiteralPath (Join-Path $runtime 'status.json')) { throw 'This launch has already been used. Preserve its evidence.' }
$readyPath = 'D:/HCUP/vg-spec1/logs/development-round-02/wfp-offline-round-01/wfp-controller-ready.json'
if (-not (Test-Path -LiteralPath $readyPath -PathType Leaf)) { throw 'Test watcher is not ready. Ask Codex to resume preparation.' }
$ready = Get-Content -LiteralPath $readyPath -Raw | ConvertFrom-Json
if ($ready.nonce -ne 'e1ac1ca3b1754039a73dff7b51e40d4e' -or $ready.operation -ne 'watch_only_no_request') {
    throw 'The watcher does not match this reviewed launch.'
}
$readyUtc = [DateTimeOffset]$ready.at
$readyAge = ([DateTimeOffset]::UtcNow - $readyUtc).TotalSeconds
if ($readyAge -lt -2 -or $readyAge -gt 1800) { throw 'The prepared test watcher has expired. Ask Codex to resume preparation.' }
$watcher = [Diagnostics.Process]::GetProcessById([int]$ready.controller_pid)
try {
    if ($watcher.HasExited -or $watcher.StartTime.ToUniversalTime() -gt $readyUtc.UtcDateTime) {
        throw 'The prepared watcher process has ended or changed.'
    }
} finally { $watcher.Dispose() }
Write-Host 'Starting the reviewed vg-spec1 temporary network test helper. Keep this window open. Ctrl+C requests cleanup.'
& 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/Start-GuardManually.ps1' `
    -TargetPid 38368 `
    -TargetStartUtc '2026-10-17T10:19:41.1394029Z' `
    -TargetSha256 '3bdccb9ded50976d16fb74510dcddf46cbab5baf62bbad1cc32a32a32922c3ff' `
    -InstanceRoot 'D:/HCUP/vg-spec1/logs/development-round-02/manual-instance/instances' `
    -RunDirectory $runtime `
    -RunNonce 'e1ac1ca3b1754039a73dff7b51e40d4e' `
    -MaxSeconds 1200 -MaxBlockSeconds 600
