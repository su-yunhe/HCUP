param([Parameter(Mandatory=$true)][string]$Device,
      [switch]$SourceFrozen,
      [string]$RunName = ('offline-' + (Get-Date -Format yyyyMMdd-HHmmss)),
      [string]$BaseManifest = 'D:/HCUP/vg-spec1/logs/development-round-01/formal-round-02/installed-hap-manifest.json',
      [string]$HdcDirectory = '',
      [ValidateSet('host-controller')][string]$ControlMode = 'host-controller',
      [ValidateRange(60,7200)][int]$HostWaitSeconds = 1800)
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
if (-not $SourceFrozen) { throw 'Require exclusive frozen production source' }
if ($RunName -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Simple fresh RunName required' }
if ($HdcDirectory) {
    if (-not (Test-Path -LiteralPath (Join-Path $HdcDirectory 'hdc.exe'))) { throw 'No hdc.exe in provided tool directory' }
    $env:PATH = $HdcDirectory + ';' + $env:PATH
}
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ($taskRoot -ne 'D:\HCUP\vg-spec1') { throw 'Scoped to vg-spec1' }
$runDirectory = Join-Path $taskRoot ('logs/development-round-02/' + $RunName)
if (Test-Path -LiteralPath $runDirectory) { throw 'Choose a fresh run directory' }
New-Item -ItemType Directory -Path $runDirectory | Out-Null
$env:PYTHONPATH = 'D:/HCUP/common/test-harness;D:/HCUP/vg-spec1'
$env:VG_RUN_DIRECTORY = $runDirectory
$env:VG_BASE_MANIFEST = $BaseManifest
$env:VG_VERIFICATION_MANIFEST = Join-Path $runDirectory 'installed-hap-manifest.json'
$env:VG_OFFLINE_DEVICE = $Device
$env:VG_TEST_DEVICE = $Device
$env:VG_OFFLINE_CONTROL = $ControlMode
$env:VG_HOST_WAIT_SECONDS = [string]$HostWaitSeconds
python -c "from hypium_tests.evidence import *; base=json.loads(Path(os.environ['VG_BASE_MANIFEST']).read_text(encoding='utf8')); assert base['source']==source_fingerprint(); assert base['hap_sha256']==digest((ROOT/'entry/build/default/outputs/default/entry-default-unsigned.hap').read_bytes()); write_json(Path(os.environ['VG_RUN_DIRECTORY'])/'source-before-install.json',source_fingerprint())"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& hdc -t $Device install -r (Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap') 2>&1 | Tee-Object -FilePath (Join-Path $runDirectory 'install.log')
$installExit = $LASTEXITCODE
$installExit | Set-Content -LiteralPath (Join-Path $runDirectory 'install.exit.txt')
if ($installExit -ne 0 -or (Select-String -LiteralPath (Join-Path $runDirectory 'install.log') -Pattern '\[Fail\]|Failure' -Quiet)) { throw 'Install failed' }
python -c "from hypium_tests.evidence import *; base=json.loads(Path(os.environ['VG_BASE_MANIFEST']).read_text(encoding='utf8')); out=Path(os.environ['VG_RUN_DIRECTORY']); assert base['source']==source_fingerprint(); base.update(installed_at=utc(),device=os.environ['VG_OFFLINE_DEVICE'],evidence_dir=out.relative_to(ROOT).as_posix(),base_manifest=os.environ['VG_BASE_MANIFEST']); write_json(Path(os.environ['VG_VERIFICATION_MANIFEST']),base)"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
New-Item -ItemType Directory (Join-Path $runDirectory 'tests-used') | Out-Null
Get-ChildItem $PSScriptRoot -File | Copy-Item -Destination (Join-Path $runDirectory 'tests-used')
Get-ChildItem (Join-Path $runDirectory 'tests-used') -File | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $runDirectory 'tests-used/sha256.json')
Push-Location $runDirectory
try {
    python -m hypium_tests.run_selected --device $Device --json (Join-Path $runDirectory 'selftest.json') hypium_tests.offline_confirmation.OfflineRestoreTests.test_13_actual_offline_three_cancels_and_restore 2>&1 | Tee-Object -FilePath (Join-Path $runDirectory 'hypium.log')
    $testExit = $LASTEXITCODE
    $testExit | Set-Content -LiteralPath (Join-Path $runDirectory 'hypium.exit.txt')
    python -c "from hypium_tests.evidence import *; out=Path(os.environ['VG_RUN_DIRECTORY']); before=json.loads((out/'source-before-install.json').read_text(encoding='utf8')); after=source_fingerprint(); write_json(out/'source-after-run.json',after); assert before==after, 'Source changed; invalidate evidence'"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    exit $testExit
} finally { Pop-Location }
