param(
    [switch]$SourceFrozen,
    [switch]$FilterExecutionApproved,
    [Parameter(Mandatory=$true)][string]$HelperManifest,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{32}$')][string]$Nonce,
    [string]$Device = '127.0.0.1:11237',
    [string]$RunName = ('wfp-offline-' + (Get-Date -Format yyyyMMdd-HHmmss)),
    [string]$RuntimeDirectory = '',
    [string]$BaseManifest = 'D:/HCUP/vg-spec1/logs/development-round-02/manual-full-round-02/installed-hap-manifest.json',
    [string]$LaunchScript = 'D:/HCUP/vg-spec1/workflow/start-reviewed-network-test.ps1',
    [string]$LaunchMetadata = 'D:/HCUP/vg-spec1/workflow/reviewed-network-launch-05.json',
    [ValidateRange(60,3600)][int]$HelperStartWaitSeconds = 1800
)
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
if (-not $SourceFrozen -or -not $FilterExecutionApproved) { throw 'Require frozen production and explicit coordinator approval of this reviewed filter experiment' }
if ($Device -ne '127.0.0.1:11237') { throw 'Only dedicated VgSpec1ManualOffline11237 is supported' }
if ($RunName -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Simple fresh RunName required' }
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ($taskRoot -ne 'D:\HCUP\vg-spec1') { throw 'Scoped to vg-spec1' }
$taskLaunchScript = [IO.Path]::GetFullPath($LaunchScript)
$taskLaunchMetadata = [IO.Path]::GetFullPath($LaunchMetadata)
foreach ($taskLaunchFile in @($taskLaunchScript, $taskLaunchMetadata)) {
    if (-not $taskLaunchFile.StartsWith(($taskRoot + '\workflow\'), [StringComparison]::OrdinalIgnoreCase) -or -not [IO.File]::Exists($taskLaunchFile)) { throw 'Reviewed launch archive input must be an existing task workflow file' }
}
$runDirectory = Join-Path $taskRoot ('logs/development-round-02/' + $RunName)
if ((Test-Path -LiteralPath (Join-Path $runDirectory 'installed-hap-manifest.json')) -or (Test-Path -LiteralPath (Join-Path $runDirectory 'selftest.json'))) { throw 'Choose fresh RunName; preserve prior results' }
New-Item -ItemType Directory -Force -Path $runDirectory | Out-Null
if (-not $RuntimeDirectory) { $RuntimeDirectory = Join-Path $runDirectory 'wfp-runtime' }
$env:PYTHONPATH = 'D:/HCUP/common/test-harness;D:/HCUP/vg-spec1'
$env:VG_RUN_DIRECTORY = $runDirectory
$env:VG_BASE_MANIFEST = $BaseManifest
$env:VG_VERIFICATION_MANIFEST = Join-Path $runDirectory 'installed-hap-manifest.json'
$env:VG_TEST_DEVICE = $Device
$env:VG_WFP_HELPER_MANIFEST = [IO.Path]::GetFullPath($HelperManifest)
$env:VG_WFP_RUNTIME = [IO.Path]::GetFullPath($RuntimeDirectory)
$env:VG_WFP_NONCE = $Nonce
$env:VG_WFP_EXECUTION_APPROVED = '1'
$env:VG_WFP_START_WAIT_SECONDS = [string]$HelperStartWaitSeconds
python -c "from hypium_tests.evidence import *; base=json.loads(Path(os.environ['VG_BASE_MANIFEST']).read_text(encoding='utf-8-sig')); helper=json.loads(Path(os.environ['VG_WFP_HELPER_MANIFEST']).read_text(encoding='utf-8-sig')); out=Path(os.environ['VG_RUN_DIRECTORY']); runtime=Path(os.environ['VG_WFP_RUNTIME']).resolve(); assert runtime.is_relative_to(out.resolve()); assert not (runtime/'request.json').exists() and not (runtime/'status.json').exists(), 'Fresh runtime required'; assert Path(os.environ['VG_WFP_HELPER_MANIFEST']).is_relative_to(ROOT); assert base['source']==source_fingerprint(); assert base['hap_sha256']==digest((ROOT/'entry/build/default/outputs/default/entry-default-unsigned.hap').read_bytes()); assert digest(Path(helper['helperExe']).read_bytes())==helper['helperSha256'].lower(); write_json(out/'source-before-install.json',source_fingerprint()); write_json(out/'reviewed-helper-manifest.json',helper)"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& hdc -t $Device install -r (Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap') 2>&1 | Tee-Object -FilePath (Join-Path $runDirectory 'install.log')
$installExit = $LASTEXITCODE
$installExit | Set-Content -LiteralPath (Join-Path $runDirectory 'install.exit.txt')
if ($installExit -ne 0 -or (Select-String -LiteralPath (Join-Path $runDirectory 'install.log') -Pattern '\[Fail\]|Failure' -Quiet)) { throw 'Fresh install failed' }
python -c "from hypium_tests.evidence import *; base=json.loads(Path(os.environ['VG_BASE_MANIFEST']).read_text(encoding='utf-8-sig')); out=Path(os.environ['VG_RUN_DIRECTORY']); assert base['source']==source_fingerprint(); base.update(installed_at=utc(),device=DEVICE,evidence_dir=out.relative_to(ROOT).as_posix(),base_manifest=os.environ['VG_BASE_MANIFEST']); write_json(Path(os.environ['VG_VERIFICATION_MANIFEST']),base)"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Recursive archive includes native source, README, build/launch scripts and EXE.
# The actual reviewed executable is also archived under an explicit name.
$archive = Join-Path $runDirectory 'tests-used'
New-Item -ItemType Directory -Path $archive | Out-Null
Get-ChildItem -LiteralPath $PSScriptRoot -File -Recurse | Where-Object { $_.FullName -notmatch '[\\/]__pycache__[\\/]|\.pyc$' } | ForEach-Object {
    $relative = $_.FullName.Substring($PSScriptRoot.Length + 1)
    $destination = Join-Path $archive $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $destination
}
$helperInfo = Get-Content -Raw -LiteralPath $HelperManifest | ConvertFrom-Json
$actualHelperArchive = Join-Path $archive 'actual-reviewed-helper'
New-Item -ItemType Directory -Path $actualHelperArchive | Out-Null
Copy-Item -LiteralPath $helperInfo.helperExe -Destination $actualHelperArchive
$launcherArchive = Join-Path $archive 'user-launcher'
New-Item -ItemType Directory -Path $launcherArchive | Out-Null
Copy-Item -LiteralPath $taskLaunchScript -Destination $launcherArchive
Copy-Item -LiteralPath $taskLaunchMetadata -Destination $launcherArchive
$helperInfo.sourceFiles | ForEach-Object {
    if ((Get-FileHash -LiteralPath (Join-Path $taskRoot $_.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $_.sha256) { throw 'Reviewed helper source changed before test' }
}
$archiveHashes = @(Get-ChildItem -LiteralPath $archive -File -Recurse | ForEach-Object { [ordered]@{path=$_.FullName.Substring($archive.Length+1).Replace('\','/');size=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} })
ConvertTo-Json -InputObject $archiveHashes -Depth 5 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $archive 'recursive-sha256.json')
Push-Location $runDirectory
try {
    python -m hypium_tests.run_selected --device $Device --json (Join-Path $runDirectory 'selftest.json') hypium_tests.wfp_offline_confirmation.WfpOfflineRestoreTests.test_19_wfp_actual_outbound_isolation_three_cancels 2>&1 | Tee-Object -FilePath (Join-Path $runDirectory 'hypium.log')
    $testExit = $LASTEXITCODE
    $testExit | Set-Content -LiteralPath (Join-Path $runDirectory 'hypium.exit.txt')
    python -c "from hypium_tests.evidence import *; out=Path(os.environ['VG_RUN_DIRECTORY']); before=json.loads((out/'source-before-install.json').read_text(encoding='utf8')); after=source_fingerprint(); write_json(out/'source-after-run.json',after); assert before==after,'Production source changed'; helper=json.loads((out/'reviewed-helper-manifest.json').read_text(encoding='utf8')); assert digest(Path(helper['helperExe']).read_bytes())==helper['helperSha256'].lower(),'Helper binary changed'; report=json.loads((out/'selftest.json').read_text(encoding='utf8')); assert len(report['cases'])==1 and all(c['outcome']=='pass' for c in report['cases']),'Supplement must be one actual pass and zero skips'"
    $auditExit = $LASTEXITCODE
    if ($testExit -ne 0) { exit $testExit }
    exit $auditExit
} finally { Pop-Location }
