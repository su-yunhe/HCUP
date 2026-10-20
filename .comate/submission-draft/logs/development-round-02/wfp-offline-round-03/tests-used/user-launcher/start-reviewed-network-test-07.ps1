#Requires -RunAsAdministrator
# vg-spec1 reviewed helper06 and controller07.1; user launches this in an already elevated PowerShell.
# No automatic RunAs/UAC, policy changes, downloads or device lifecycle operations.
$ErrorActionPreference = 'Stop'
$root = 'D:/HCUP/vg-spec1'
$freeze = 'D:/HCUP/vg-spec1/logs/development-round-03/wfp-build/20261017-185653-924dfb/frozen-review-06-fingerprint.json'
if ((Get-FileHash -LiteralPath $freeze -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'cf6a31890172a658666cb390db404fa45c19edb900d062565548909f80531250') {
    throw 'The reviewed helper source manifest changed. Do not launch.'
}
$reviewed = Get-Content -LiteralPath $freeze -Raw | ConvertFrom-Json
foreach ($source in $reviewed.sources) {
    if ((Get-FileHash -LiteralPath (Join-Path $root $source.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $source.sha256) {
        throw ('Reviewed helper source changed: ' + $source.path)
    }
}
$exe = 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/bin/VgSpec1WfpGuard.exe'
if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'c62ce4afcdf172ecda02b31a6c006f4f4cca92346328d158b97409cd14acc8ff') {
    throw 'The reviewed helper executable changed. Do not launch.'
}
$approvedTestFiles = @{
    'hypium_tests/wfp_controller.py' = '919a3304b9efa32ef4a0a40e6227049ad2d495cea3a20be688250b984cbc0958'
    'hypium_tests/wfp_offline_confirmation.py' = 'b0ae62334cfcf8373d10df3ecf6f057dbc61b8b38d5dc88c1f9c9722e049d87e'
    'hypium_tests/run_wfp_offline.ps1' = '0c767653d099a739f6cf5247584532fbc7c82fb8dca31fad5976a1fc7f0a604f'
    'hypium_tests/lifecycle_regression.py' = 'e4d47884dfeb224552ede95fc2888a0efbe840c1929818bf238f0272d9742155'
}
foreach ($relativePath in $approvedTestFiles.Keys) {
    if ((Get-FileHash -LiteralPath (Join-Path $root $relativePath) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $approvedTestFiles[$relativePath]) {
        throw ('Reviewed test source changed: ' + $relativePath)
    }
}
$runtime = 'D:/HCUP/vg-spec1/logs/development-round-02/wfp-offline-round-03/wfp-runtime'
if (-not (Test-Path -LiteralPath $runtime -PathType Container)) { throw 'Test watcher is not prepared.' }
if (Test-Path -LiteralPath (Join-Path $runtime 'status.json')) { throw 'This launch has already been used. Preserve its evidence.' }
$readyPath = 'D:/HCUP/vg-spec1/logs/development-round-02/wfp-offline-round-03/wfp-controller-ready.json'
if (-not (Test-Path -LiteralPath $readyPath -PathType Leaf)) { throw 'Test watcher is not ready. Ask Codex to resume preparation.' }
$ready = Get-Content -LiteralPath $readyPath -Raw | ConvertFrom-Json
if ($ready.nonce -ne '348b3a916fe546f7b7a5b215bda4ec8c' -or $ready.operation -ne 'watch_only_no_request') {
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
    -RunNonce '348b3a916fe546f7b7a5b215bda4ec8c' `
    -MaxSeconds 1200 -MaxBlockSeconds 600
