param(
    [switch]$SourceFrozen,
    [string]$RunName = 'formal-round-01',
    [string]$Device = '127.0.0.1:11235',
    [ValidateSet('development-round-01','development-round-02')]
    [string]$EvidenceRound = 'development-round-01'
)

. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
if (-not $SourceFrozen) {
    throw 'Require exclusive source access during verification. Use -SourceFrozen after all editors have stopped.'
}
if ($RunName -notmatch '^[a-zA-Z0-9_-]+$') { throw 'RunName must be one simple directory name' }
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ($taskRoot -ne 'D:\HCUP\vg-spec1') { throw 'This verification script is scoped to vg-spec1' }
$runDirectory = Join-Path $taskRoot ('logs/' + $EvidenceRound + '/' + $RunName)
if (Test-Path -LiteralPath (Join-Path $runDirectory 'selftest.json')) {
    throw 'This run already has a report; choose a fresh -RunName to preserve raw evidence'
}
New-Item -ItemType Directory -Force -Path $runDirectory | Out-Null
$env:VG_RUN_DIRECTORY = $runDirectory
$env:VG_TEST_DEVICE = $Device
$env:PYTHONPATH = 'D:/HCUP/common/test-harness;D:/HCUP/vg-spec1'
$env:VG_VERIFICATION_MANIFEST = Join-Path $runDirectory 'installed-hap-manifest.json'
Push-Location $taskRoot
try {
    python -c "from hypium_tests.evidence import *; out=Path(os.environ['VG_RUN_DIRECTORY']); write_json(out/'source-before-build.json', source_fingerprint())"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & hvigorw --mode module -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon 2>&1 |
        Tee-Object -FilePath (Join-Path $runDirectory 'build.log')
    $buildExit = $LASTEXITCODE
    $buildExit | Set-Content -LiteralPath (Join-Path $runDirectory 'build.exit.txt')
    if ($buildExit -ne 0) { exit $buildExit }

    $hapPath = Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
    Get-Item -LiteralPath $hapPath | Select-Object FullName,Length,LastWriteTimeUtc |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDirectory 'hap-file.json')
    Get-FileHash -Algorithm SHA256 -LiteralPath $hapPath | ConvertTo-Json |
        Set-Content -LiteralPath (Join-Path $runDirectory 'hap-sha256.json')

    & hdc -t $Device install -r $hapPath 2>&1 | Tee-Object -FilePath (Join-Path $runDirectory 'install.log')
    $installExit = $LASTEXITCODE
    $installExit | Set-Content -LiteralPath (Join-Path $runDirectory 'install.exit.txt')
    if ($installExit -ne 0 -or (Select-String -LiteralPath (Join-Path $runDirectory 'install.log') -Pattern '\[Fail\]|Failure' -Quiet)) {
        throw 'Freshly built HAP did not install successfully'
    }
    python -c "from hypium_tests.evidence import *; out=Path(os.environ['VG_RUN_DIRECTORY']); before=json.loads((out/'source-before-build.json').read_text(encoding='utf8')); current=source_fingerprint(); assert current==before, 'SOURCE CHANGED DURING BUILD; INVALID'; hap=ROOT/'entry/build/default/outputs/default/entry-default-unsigned.hap'; write_json(Path(os.environ['VG_VERIFICATION_MANIFEST']), {'coordinator_frozen':True,'installed_at':utc(),'device':DEVICE,'source':current,'hap_sha256':digest(hap.read_bytes()),'evidence_dir':out.relative_to(ROOT).as_posix()})"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Push-Location $runDirectory
    try {
        python -m harness.runner --project $taskRoot --device $Device --json (Join-Path $runDirectory 'selftest.json') 2>&1 |
            Tee-Object -FilePath (Join-Path $runDirectory 'hypium.log')
        $testExit = $LASTEXITCODE
        $testExit | Set-Content -LiteralPath (Join-Path $runDirectory 'hypium.exit.txt')
    } finally { Pop-Location }
    python -c "from hypium_tests.evidence import *; out=Path(os.environ['VG_RUN_DIRECTORY']); before=json.loads((out/'source-before-build.json').read_text(encoding='utf8')); after=source_fingerprint(); write_json(out/'source-after-run.json',after); assert before==after,'SOURCE CHANGED; INVALIDATE RUN'; report=json.loads((out/'selftest.json').read_text(encoding='utf8')); assert len(report.get('cases',[]))>=13, 'Missing discovered test cases'; assert not any(c.get('outcome','').lower() in ('skip','skipped') for c in report.get('cases',[])), 'Skipped cases are NOT acceptance passes'"
    $auditExit = $LASTEXITCODE
    if ($testExit -ne 0) { exit $testExit }
    exit $auditExit
} finally { Pop-Location }
