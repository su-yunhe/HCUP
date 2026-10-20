param(
  [ValidateSet('Build', 'Run')][string]$Action,
  [string]$RunId = (Get-Date -Format 'yyyyMMdd-HHmmss'),
  [string]$Device = '127.0.0.1:5555'
)
$ErrorActionPreference = 'Stop'
. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$taskRoot = 'D:/HCUP/vg-spec9'
Set-Location -LiteralPath $taskRoot
$traceRoot = Join-Path $taskRoot "traces/implementation-validation/$RunId"
New-Item -ItemType Directory -Path $traceRoot -Force | Out-Null
Start-Transcript -Path (Join-Path $traceRoot "$Action-command.log") -Force
try {
  if ($env:VGSPEC9_SOURCE_FROZEN -ne '1') { throw 'Main-agent source freeze and shared-device lease must be confirmed first.' }
  $env:HDC_DEVICE = $Device
  $env:PYTHONPATH = 'D:/HCUP/common/test-harness;D:/HCUP/vg-spec9'
  $env:VGSPEC9_EVIDENCE = $traceRoot
  Copy-Item -LiteralPath (Join-Path $taskRoot 'hypium_tests/test_webdav_loading.py') -Destination (Join-Path $traceRoot 'test-source-used.py')
  & 'D:/HCUP/common/.venv/Scripts/python.exe' -c "from hypium_tests.evidence import source_fingerprint,save; save('source-fingerprint-command-before.json',source_fingerprint())"
  if ($LASTEXITCODE -ne 0) { throw "Fingerprint failed: $LASTEXITCODE" }
  if ($Action -eq 'Build') {
    Write-Output 'COMMAND: hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon'
    & hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | Tee-Object -FilePath (Join-Path $traceRoot 'build-raw.log')
    $taskExit = $LASTEXITCODE
    Set-Content -LiteralPath (Join-Path $traceRoot 'build-exit.txt') -Value $taskExit
    if ($taskExit -ne 0) { throw "Build failed: $taskExit" }
    Get-FileHash -Algorithm SHA256 -LiteralPath 'entry/build/default/outputs/default/entry-default-unsigned.hap' | Format-List
  } else {
    $taskHap = Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
    Get-FileHash -Algorithm SHA256 -LiteralPath $taskHap | Format-List
    Write-Output "COMMAND: hdc -t $Device install -r $taskHap"
    & hdc -t $Device install -r $taskHap
    $taskInstallExit = $LASTEXITCODE
    Write-Output "INSTALL_EXIT=$taskInstallExit"
    if ($taskInstallExit -ne 0) { throw "Install failed: $taskInstallExit" }
    New-Item -ItemType Directory -Path (Join-Path $taskRoot 'logs') -Force | Out-Null
    Set-Location -LiteralPath (Join-Path $taskRoot 'logs')
    Write-Output "COMMAND: D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project $taskRoot --device $Device --json $traceRoot/selftest.json"
    & 'D:/HCUP/common/.venv/Scripts/python.exe' -m harness.runner --project $taskRoot --device $Device --json (Join-Path $traceRoot 'selftest.json') 2>&1 | Tee-Object -FilePath (Join-Path $traceRoot 'selftest-raw.log')
    $taskExit = $LASTEXITCODE
    Set-Content -LiteralPath (Join-Path $traceRoot 'selftest-exit.txt') -Value $taskExit
  }
  & 'D:/HCUP/common/.venv/Scripts/python.exe' -c "from hypium_tests.evidence import source_fingerprint,save; save('source-fingerprint-command-after.json',source_fingerprint())"
  Write-Output "ACTION_EXIT=$taskExit"
} finally {
  Set-Location -LiteralPath $taskRoot
  Stop-Transcript
}
exit $taskExit
