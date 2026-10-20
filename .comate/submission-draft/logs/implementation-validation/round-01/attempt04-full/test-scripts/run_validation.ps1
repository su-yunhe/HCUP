param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9-]+$')][string]$Attempt,
    [ValidateSet('smoke','full')][string]$Mode='full'
)
. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
$ErrorActionPreference='Stop'
$taskRoot='D:/HCUP/vg-spec8'
$roundRoot="$taskRoot/logs/implementation-validation/round-01"
$attemptRoot="$roundRoot/$Attempt"
if (Test-Path -LiteralPath $attemptRoot) { throw "Evidence directory already exists: $attemptRoot" }
New-Item -ItemType Directory -Path $attemptRoot | Out-Null
Set-Location -LiteralPath $taskRoot
$env:PYTHONPATH='D:/HCUP/common/test-harness;D:/HCUP/vg-spec8'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:VG_SPEC8_RELEASED='yes'
$env:VG_SPEC8_LOG_DIR=$attemptRoot
$env:HDC_DEVICE='127.0.0.1:5555'
Copy-Item -LiteralPath "$roundRoot/source-fingerprint-before.json" -Destination "$attemptRoot/source-fingerprint-before.json"
& D:/HCUP/common/.venv/Scripts/python.exe -c "from hypium_tests.verification_support import source_fingerprint,write_json; import json,pathlib,os; p=pathlib.Path(os.environ['VG_SPEC8_LOG_DIR']); expected=json.loads((p/'source-fingerprint-before.json').read_text(encoding='utf-8-sig')); actual=source_fingerprint(); write_json('source-integrity-pre-run.json',{'same':expected==actual,'count':len(actual)}); assert expected==actual"
if ($LASTEXITCODE -ne 0) { throw 'Production fingerprint changed' }
hdc -t 127.0.0.1:5555 shell aa force-stop io.qzz.weiyu *> "$attemptRoot/force-stop.log"
hdc -t 127.0.0.1:5555 shell bm dump -n io.qzz.weiyu *> "$attemptRoot/bm-before-install.json"
$hapRelative='entry/build/default/outputs/default/entry-default-unsigned.hap'
$installCommand="hdc -t 127.0.0.1:5555 install -r $hapRelative"
$installCommand | Set-Content -LiteralPath "$attemptRoot/install-command.txt" -Encoding utf8
hdc -t 127.0.0.1:5555 install -r $hapRelative *> "$attemptRoot/install.log"
$installExit=$LASTEXITCODE
hdc -t 127.0.0.1:5555 shell bm dump -n io.qzz.weiyu *> "$attemptRoot/bm-after-install.json"
$beforeText=Get-Content -LiteralPath "$attemptRoot/bm-before-install.json" -Raw
$afterText=Get-Content -LiteralPath "$attemptRoot/bm-after-install.json" -Raw
$beforeTime=[regex]::Match($beforeText,'"updateTime"\s*:\s*(\d+)').Groups[1].Value
$afterTime=[regex]::Match($afterText,'"updateTime"\s*:\s*(\d+)').Groups[1].Value
$installText=Get-Content -LiteralPath "$attemptRoot/install.log" -Raw
$success=($installExit -eq 0 -and $installText -match 'success' -and $installText -notmatch '\[Fail\]' -and $beforeTime -ne $afterTime)
$hapPath=(Resolve-Path -LiteralPath $hapRelative).Path
@{device='127.0.0.1:5555';hapPath=$hapPath;hapSha256=(Get-FileHash -LiteralPath $hapPath -Algorithm SHA256).Hash.ToLower();buildExitCode=0;buildEvidence='../build-result.json';installExitCode=$installExit;installSemanticSuccess=$success;bmBeforeUpdateTime=$beforeTime;bmAfterUpdateTime=$afterTime;time=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath "$attemptRoot/installation-manifest.json" -Encoding utf8
Get-Content -LiteralPath "$attemptRoot/install.log"
if (-not $success) { throw 'Install result is not semantically successful' }
Set-Location -LiteralPath $attemptRoot
$testStart=Get-Date
if ($Mode -eq 'smoke') {
    'D:/HCUP/common/.venv/Scripts/python.exe -m unittest hypium_tests.test_restore_confirmation.RestoreConfirmationTests.test_01_core_smoke -v' | Set-Content -LiteralPath "$attemptRoot/test-command.txt" -Encoding utf8
    & D:/HCUP/common/.venv/Scripts/python.exe -m unittest hypium_tests.test_restore_confirmation.RestoreConfirmationTests.test_01_core_smoke -v *> "$attemptRoot/harness.log"
} else {
    'D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project D:/HCUP/vg-spec8 --device 127.0.0.1:5555 --json harness-report.json' | Set-Content -LiteralPath "$attemptRoot/test-command.txt" -Encoding utf8
    & D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project D:/HCUP/vg-spec8 --device 127.0.0.1:5555 --json "$attemptRoot/harness-report.json" *> "$attemptRoot/harness.log"
}
$testExit=$LASTEXITCODE
@{exitCode=$testExit;mode=$Mode;start=$testStart.ToString('o');finish=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath "$attemptRoot/test-process.json" -Encoding utf8
Get-Content -LiteralPath "$attemptRoot/harness.log" -Tail 45
exit $testExit
