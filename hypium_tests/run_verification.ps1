param([string]$RunLabel = 'core-v1', [string]$Cases = '')
$ErrorActionPreference = 'Continue'
. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location -LiteralPath 'D:/HCUP/vg-spec7'
$runLogs = "logs/do-$RunLabel"
New-Item -ItemType Directory -Path $runLogs -Force | Out-Null
$env:VG7_EVIDENCE_DIR = "D:/HCUP/vg-spec7/traces/do-verification/$RunLabel"
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUNBUFFERED = '1'
$env:PYTHONPATH = 'D:/HCUP/common/test-harness'
$env:VG7_CASES = $Cases
$hapFile = (Resolve-Path -LiteralPath 'entry/build/default/outputs/default/entry-default-unsigned.hap').Path
$buildSources = Get-Content 'traces/do-verification-build-v1/source-after.json' -Raw | ConvertFrom-Json
foreach ($entry in $buildSources.PSObject.Properties) {
  if ((Get-FileHash -LiteralPath $entry.Name -Algorithm SHA256).Hash.ToLower() -ne $entry.Value) {
    throw "Production file changed since independent build: $($entry.Name)"
  }
}
$installRecord = [ordered]@{start=(Get-Date -Format o); command=@('hdc','-t','127.0.0.1:5555','install','-r',$hapFile); hap_sha256=(Get-FileHash $hapFile -Algorithm SHA256).Hash.ToLower()}
& hdc list targets 2>&1 | Set-Content "$runLogs/targets.log" -Encoding utf8
$installOutput = & hdc -t 127.0.0.1:5555 install -r $hapFile 2>&1
$installRecord.exit_code = $LASTEXITCODE
$installOutput | Tee-Object -FilePath "$runLogs/install.log"
$installRecord.success_message = ($installOutput | Out-String) -match 'install bundle successfully'
$installRecord.end = Get-Date -Format o
$installRecord | ConvertTo-Json -Depth 5 | Set-Content "$runLogs/install.json" -Encoding utf8
if ($installRecord.exit_code -ne 0 -or -not $installRecord.success_message) { exit 1 }
& hdc -t 127.0.0.1:5555 shell 'bm dump -n io.qzz.weiyu' 2>&1 | Set-Content "$runLogs/installed-bundle.log" -Encoding utf8
$runRecord = [ordered]@{start=(Get-Date -Format o); cwd='D:/HCUP/vg-spec7/logs'; command=@('D:/HCUP/common/.venv/Scripts/python.exe','-m','harness.runner','--project','D:/HCUP/vg-spec7','--device','127.0.0.1:5555','--json',"D:/HCUP/vg-spec7/$runLogs/selftest.json"); evidence_dir=$env:VG7_EVIDENCE_DIR; explicitly_selected_cases=$Cases}
Set-Location -LiteralPath 'D:/HCUP/vg-spec7/logs'
& 'D:/HCUP/common/.venv/Scripts/python.exe' -m harness.runner --project D:/HCUP/vg-spec7 --device 127.0.0.1:5555 --json "D:/HCUP/vg-spec7/$runLogs/selftest.json" 2>&1 | Tee-Object -FilePath "D:/HCUP/vg-spec7/$runLogs/selftest.log" | Out-Null
$testCode = $LASTEXITCODE
$runRecord.end = Get-Date -Format o
$runRecord.exit_code = $testCode
$runRecord | ConvertTo-Json -Depth 5 | Set-Content "D:/HCUP/vg-spec7/$runLogs/invocation.json" -Encoding utf8
Write-Output "harness exit_code=$testCode"
Get-Content "D:/HCUP/vg-spec7/$runLogs/selftest.log" -Tail 24
exit $testCode
