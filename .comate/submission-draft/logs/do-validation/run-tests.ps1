param([int]$Run = 3, [string]$Case = '')
. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
. D:/HCUP/vg-spec14/logs/do-validation/device-helpers.ps1
$taskRoot = 'D:/HCUP/vg-spec14'
$hapPath = (Resolve-Path (Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap')).Path
Invoke-Vg14Hdc @('install','-r',$hapPath) | Tee-Object -FilePath (Join-Path $taskRoot "logs/do-validation/install-run-$Run.log")
Invoke-Vg14Hdc @('shell','bm','dump','-n','io.qzz.weiyu') | Set-Content -Encoding utf8 (Join-Path $taskRoot "logs/do-validation/bundle-installed-run-$Run.txt")
Get-FileHash -Algorithm SHA256 -LiteralPath $hapPath | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $taskRoot "logs/do-validation/hap-run-$Run.json")
$env:PYTHONPATH = 'D:/HCUP/common/test-harness'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:VG14_TEST_AUTHORIZED = '1'
$env:HDC_DEVICE = '127.0.0.1:5555'
$env:VG14_EVIDENCE = "$taskRoot/logs/do-validation/device-run-v$Run"
$env:VG14_CASE_FILTER = $Case
$recordedCommand = "D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project $taskRoot --device 127.0.0.1:5555 --json $taskRoot/logs/do-validation/runner-v$Run.json"
if ($Case) { $recordedCommand = "VG14_CASE_FILTER=$Case D:/HCUP/common/.venv/Scripts/python.exe $taskRoot/logs/do-validation/run-selected.py --project $taskRoot --device 127.0.0.1:5555 --json $taskRoot/logs/do-validation/runner-v$Run.json" }
$recordedCommand | Set-Content -Encoding utf8 (Join-Path $taskRoot "logs/do-validation/runner-v$Run.command.txt")
Push-Location (Join-Path $taskRoot 'logs')
try {
  if ($Case) {
    & 'D:/HCUP/common/.venv/Scripts/python.exe' "$taskRoot/logs/do-validation/run-selected.py" --project $taskRoot --device '127.0.0.1:5555' --json "$taskRoot/logs/do-validation/runner-v$Run.json" 2>&1 | Tee-Object -FilePath "do-validation/runner-v$Run.log"
  } else {
    & 'D:/HCUP/common/.venv/Scripts/python.exe' -m harness.runner --project $taskRoot --device '127.0.0.1:5555' --json "$taskRoot/logs/do-validation/runner-v$Run.json" 2>&1 | Tee-Object -FilePath "do-validation/runner-v$Run.log"
  }
  $runnerExit = $LASTEXITCODE
  $runnerExit | Set-Content -Encoding utf8 "do-validation/runner-v$Run.exit.txt"
} finally { Pop-Location }
exit $runnerExit
