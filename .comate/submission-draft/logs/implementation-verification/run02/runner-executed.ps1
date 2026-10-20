param(
  [Parameter(Mandatory=$true)][string]$RunId,
  [Parameter(Mandatory=$true)][string]$ExclusiveLease,
  [string]$Device = '127.0.0.1:5555'
)

. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
$verificationRoot = 'D:/HCUP/vg-spec13'
Set-Location -LiteralPath $verificationRoot
if ($RunId -notmatch '^[a-zA-Z0-9_-]+$') { throw 'RunId must be a simple filename segment' }
$verificationDir = Join-Path $verificationRoot "logs/implementation-verification/$RunId"
New-Item -ItemType Directory -Path $verificationDir -Force | Out-Null
Start-Transcript -Path (Join-Path $verificationDir 'commands.log')
$verificationStarted = Get-Date
$verificationResult = [ordered]@{
  run_id=$RunId; thread_id=$env:CODEX_THREAD_ID; exclusive_lease=$ExclusiveLease;
  started_utc=$verificationStarted.ToUniversalTime().ToString('o'); device=$Device;
  build_exit=$null; install_exit=$null; test_exit=$null; source_unchanged=$null
}
function Save-Result {
  $verificationResult | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $verificationDir 'run-result.json') -Encoding utf8
}
function Source-Hashes {
  $verificationPaths = @(rg --files entry/src AppScope hvigor) + @(Get-ChildItem -LiteralPath $verificationRoot -File -Filter '*.json5' | ForEach-Object { $_.Name })
  $verificationHashes = [ordered]@{}
  foreach ($verificationPath in ($verificationPaths | Sort-Object -Unique)) {
    if ((Split-Path $verificationPath -Leaf) -eq 'BuildProfile.ets') { continue }
    $verificationHashes[$verificationPath.Replace('\','/')] = (Get-FileHash -LiteralPath $verificationPath -Algorithm SHA256).Hash
  }
  return $verificationHashes
}
Save-Result
try {
  # Coordination authorization is supplied by the parent. This additionally
  # refuses visible competing test runners and existing fixture port ownership.
  $verificationCompetitors = @(Get-CimInstance Win32_Process | Where-Object {
    $_.ProcessId -ne $PID -and $_.Name -match 'python|node' -and
    $_.CommandLine -match 'harness\.runner|uitest|hypium_tests[\\/]test_'
  } | Select-Object ProcessId,Name)
  ConvertTo-Json -InputObject $verificationCompetitors | Set-Content (Join-Path $verificationDir 'competing-runners.json')
  if ($verificationCompetitors.Count -gt 0) { throw 'Competing test process detected; device lease must be checked' }
  $verificationListeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18173,18174,18175) } | Select-Object LocalAddress,LocalPort,OwningProcess)
  ConvertTo-Json -InputObject $verificationListeners | Set-Content (Join-Path $verificationDir 'fixture-ports-before.json')
  if ($verificationListeners.Count -gt 0) { throw 'Fixture/refusal-test ports already owned; do not displace another process' }
  hdc list targets 2>&1 | Tee-Object (Join-Path $verificationDir 'devices.log')
  if ($LASTEXITCODE -ne 0) { throw 'hdc discovery failed' }
  hdc -t $Device shell ps -ef 2>&1 | Set-Content (Join-Path $verificationDir 'device-processes-before.log')
  hdc -t $Device shell param get const.product.software.version 2>&1 | Set-Content (Join-Path $verificationDir 'device-version.log')
  hdc -t $Device shell param get const.ohos.apiversion 2>&1 | Set-Content (Join-Path $verificationDir 'device-api.log')
  hdc -t $Device shell hidumper -s WindowManagerService -a '-a' 2>&1 | Set-Content (Join-Path $verificationDir 'device-windows-before.log')
  $verificationBefore = Source-Hashes
  $verificationBefore | ConvertTo-Json | Set-Content (Join-Path $verificationDir 'source-before-build.json')
  git status --porcelain=v1 | Set-Content (Join-Path $verificationDir 'git-status-before.txt')
  hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon 2>&1 | Tee-Object (Join-Path $verificationDir 'build-raw.log')
  $verificationResult.build_exit = $LASTEXITCODE
  Save-Result
  if ($verificationResult.build_exit -ne 0) { throw "Build failed: $($verificationResult.build_exit)" }
  $verificationHap = Join-Path $verificationRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
  Get-FileHash -LiteralPath $verificationHap -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content (Join-Path $verificationDir 'hap-sha256.json')
  hdc -t $Device install -r $verificationHap 2>&1 | Tee-Object (Join-Path $verificationDir 'install.log')
  $verificationResult.install_exit = $LASTEXITCODE
  Save-Result
  if ($verificationResult.install_exit -ne 0) { throw "Install failed: $($verificationResult.install_exit)" }
  hdc -t $Device shell bm dump -n io.qzz.weiyu 2>&1 | Set-Content (Join-Path $verificationDir 'installed-bundle.log')
  hdc -t $Device fport ls 2>&1 | Set-Content (Join-Path $verificationDir 'rport-before.log')
  $verificationPorts = Get-Content (Join-Path $verificationDir 'rport-before.log') -Raw
  if ($verificationPorts -match '18173|18174|18175') { throw 'Pre-existing reverse ports conflict; parent must resolve ownership' }
  $verificationAddedPorts = @()
  try {
    foreach ($verificationPort in @(18173,18174)) {
      hdc -t $Device rport "tcp:$verificationPort" "tcp:$verificationPort" 2>&1 | Tee-Object (Join-Path $verificationDir "rport-add-$verificationPort.log")
      if ($LASTEXITCODE -ne 0) { throw "rport failed for $verificationPort" }
      $verificationAddedPorts += $verificationPort
    }
    $env:PYTHONPATH = 'D:/HCUP/common/test-harness;D:/HCUP/vg-spec13'
    $env:VG13_EVIDENCE_DIR = $verificationDir
    $env:VG13_RUN_TAG = $RunId
    Set-Location -LiteralPath $verificationDir
    & D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project $verificationRoot --device $Device --json (Join-Path $verificationDir 'selftest.json') 2>&1 | Tee-Object (Join-Path $verificationDir 'selftest-raw.log')
    $verificationResult.test_exit = $LASTEXITCODE
    Save-Result
    hdc -t $Device shell hilog -x 2>&1 | Set-Content (Join-Path $verificationDir 'device-hilog.log')
  } finally {
    Set-Location -LiteralPath $verificationRoot
    foreach ($verificationPort in $verificationAddedPorts) {
      hdc -t $Device fport rm "tcp:$verificationPort" "tcp:$verificationPort" 2>&1 | Tee-Object (Join-Path $verificationDir "rport-remove-$verificationPort.log")
    }
    hdc -t $Device fport ls 2>&1 | Set-Content (Join-Path $verificationDir 'rport-after.log')
  }
} catch {
  $verificationResult.error = $_.ToString()
  $_ | Out-String | Set-Content (Join-Path $verificationDir 'execution-error.log')
  Write-Output "VERIFICATION_ERROR=$($_.Exception.Message)"
} finally {
  Set-Location -LiteralPath $verificationRoot
  $verificationAfter = Source-Hashes
  $verificationAfter | ConvertTo-Json | Set-Content (Join-Path $verificationDir 'source-after-run.json')
  if ($verificationBefore) {
    $verificationResult.source_unchanged = (($verificationBefore | ConvertTo-Json -Compress) -eq ($verificationAfter | ConvertTo-Json -Compress))
  }
  git status --porcelain=v1 | Set-Content (Join-Path $verificationDir 'git-status-after.txt')
  @(Get-ChildItem -LiteralPath (Join-Path $verificationRoot 'entry/build'),(Join-Path $verificationRoot '.hvigor') -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $verificationStarted } | ForEach-Object { [ordered]@{path=$_.FullName.Substring($verificationRoot.Length+1); length=$_.Length; modified_utc=$_.LastWriteTimeUtc.ToString('o')} }) | ConvertTo-Json | Set-Content (Join-Path $verificationDir 'build-generated-files.json')
  $verificationResult.ended_utc = (Get-Date).ToUniversalTime().ToString('o')
  Save-Result
  Stop-Transcript
}
if ($verificationResult.error -or $verificationResult.build_exit -ne 0 -or $verificationResult.install_exit -ne 0 -or $verificationResult.test_exit -ne 0 -or -not $verificationResult.source_unchanged) { exit 1 }
exit 0
