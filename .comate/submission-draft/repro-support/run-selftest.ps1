param(
  [string]$Device = '127.0.0.1:5555',
  [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$taskDir = Split-Path -Parent $PSScriptRoot
$projectDir = Join-Path $taskDir 'project'
if (-not (Test-Path -LiteralPath (Join-Path $projectDir 'hypium_tests/test_webdav_backup.py'))) {
  throw 'Run from packaged tasks/vg-spec13/repro-support with a sibling project directory.'
}
$pythonExe = (Get-Command $Python -ErrorAction Stop).Source
$listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18173,18174,18175) })
if ($listeners.Count -gt 0) { throw 'Fixture ports already owned; use an idle exclusive test environment.' }
$ports = (& hdc -t $Device fport ls 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0) { throw 'Device discovery failed' }
if ($ports -match '18173|18174') { throw 'Device reverse mappings already owned; do not displace another task.' }
$addedPorts = @()
$originalDir = Get-Location
$logDir = Join-Path $taskDir ('repro-logs/' + (Get-Date -Format 'yyyyMMdd-HHmmss-ffff'))
New-Item -ItemType Directory -Path $logDir | Out-Null
$previousPythonPath = $env:PYTHONPATH
$previousEvidence = $env:VG13_EVIDENCE_DIR
$previousTag = $env:VG13_RUN_TAG
$previousBytecode = $env:PYTHONDONTWRITEBYTECODE
$testExit = 1
try {
  foreach ($port in @(18173,18174)) {
    hdc -t $Device rport "tcp:$port" "tcp:$port"
    if ($LASTEXITCODE -ne 0) { throw "Reverse mapping failed: $port" }
    $addedPorts += $port
  }
  $env:PYTHONPATH = (Join-Path $PSScriptRoot 'test-harness') + ';' + $projectDir
  $env:PYTHONDONTWRITEBYTECODE = '1'
  $env:VG13_EVIDENCE_DIR = $logDir
  $env:VG13_RUN_TAG = Split-Path -Leaf $logDir
  Set-Location -LiteralPath $logDir
  & $pythonExe -m harness.runner --project $projectDir --device $Device --json (Join-Path $logDir 'selftest.json') 2>&1 | Tee-Object -FilePath (Join-Path $logDir 'selftest-raw.log')
  $testExit = $LASTEXITCODE
} finally {
  Set-Location -LiteralPath $originalDir
  foreach ($port in $addedPorts) { hdc -t $Device fport rm "tcp:$port" "tcp:$port" }
  $env:PYTHONPATH = $previousPythonPath
  $env:VG13_EVIDENCE_DIR = $previousEvidence
  $env:VG13_RUN_TAG = $previousTag
  $env:PYTHONDONTWRITEBYTECODE = $previousBytecode
}
if ($testExit -ne 0) { throw "Self-test failed (exit $testExit); inspect $logDir" }
