param([string]$Cases = '', [string]$Run = '01')
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
$projectRoot = 'D:/HCUP/vg-spec15'
$evidenceRoot = "$projectRoot/logs/implementation-validation"
Set-Location -LiteralPath $projectRoot
$hapCandidate = "$projectRoot/entry/build/default/outputs/default/entry-default-unsigned.hap"
if (-not (Test-Path -LiteralPath $hapCandidate)) { throw 'Fresh debug HAP missing' }
$hapPath = (Get-Item -LiteralPath $hapCandidate).FullName
$hapHash = (Get-FileHash -LiteralPath $hapPath -Algorithm SHA256).Hash.ToLowerInvariant()
$hapTime = (Get-Item -LiteralPath $hapPath).LastWriteTimeUtc.ToString('o')
$started = (Get-Date).ToUniversalTime().ToString('o')
& D:/HCUP/common/.venv/Scripts/python.exe hypium_tests/audit.py "source-before-run-$Run"
& hdc -t 127.0.0.1:5555 install -r $hapPath *> "$evidenceRoot/install-$Run.raw.log"
$installExit = $LASTEXITCODE
$installText = Get-Content -LiteralPath "$evidenceRoot/install-$Run.raw.log" -Raw
[ordered]@{ command=@('hdc','-t','127.0.0.1:5555','install','-r',$hapPath); started=$started; exit_code=$installExit; success_text=($installText -match 'successfully|Success'); hap_sha256=$hapHash; hap_modified_utc=$hapTime } | ConvertTo-Json | Set-Content -LiteralPath "$evidenceRoot/install-$Run.json" -Encoding utf8
if ($installExit -ne 0 -or $installText -notmatch 'successfully|Success' -or $installText -match '\[Fail\]|failed|error:') { throw "Install not confirmed: $installText" }
& hdc -t 127.0.0.1:5555 rport tcp:18165 tcp:18165 *> "$evidenceRoot/rport-$Run.raw.log"
if ($LASTEXITCODE -ne 0) { throw 'rport mapping failed' }
$env:PYTHONPATH = 'D:/HCUP/common/test-harness'
$env:VG15_CASES = $Cases
$env:VG15_RUN = $Run
$env:PYTHONIOENCODING = 'utf-8'
try {
  Set-Location -LiteralPath "$projectRoot/logs"
  & D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project $projectRoot --device 127.0.0.1:5555 --json "$evidenceRoot/selftest-$Run.json" *> "$evidenceRoot/selftest-$Run.raw.log"
  $testExit = $LASTEXITCODE
} finally {
  Set-Location -LiteralPath $projectRoot
  & hdc -t 127.0.0.1:5555 fport rm tcp:18165 tcp:18165 *> "$evidenceRoot/rport-cleanup-$Run.raw.log"
  & D:/HCUP/common/.venv/Scripts/python.exe hypium_tests/audit.py "source-after-run-$Run"
}
[ordered]@{ command=@('D:/HCUP/common/.venv/Scripts/python.exe','-m','harness.runner','--project',$projectRoot,'--device','127.0.0.1:5555','--json',"$evidenceRoot/selftest-$Run.json"); started=$started; finished=(Get-Date).ToUniversalTime().ToString('o'); exit_code=$testExit; cases=$Cases; hap_sha256=$hapHash } | ConvertTo-Json | Set-Content -LiteralPath "$evidenceRoot/selftest-$Run-command.json" -Encoding utf8
Get-Content -LiteralPath "$evidenceRoot/selftest-$Run.raw.log" -Tail 65
exit $testExit
