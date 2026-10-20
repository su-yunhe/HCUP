param(
    [Parameter(Mandatory=$true)][string]$RoundName,
    [Parameter(Mandatory=$true)][string]$ExpectedSourceSha256,
    [string]$Device='127.0.0.1:5555',
    [ValidateSet('capture','suite')][string]$Mode='capture',
    [string]$VisualReview='',
    [string]$BuiltManifest='',
    [ValidateSet('0','1','2','3','')][string]$InitialRotation='',
    [ValidateSet('full','smoke','layout','documents')][string]$SuiteKind='full',
    [switch]$AllowRotation
)
$ErrorActionPreference='Stop'
. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location 'D:/HCUP/cml-spec7'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH='D:/HCUP/common/test-harness;D:/HCUP/cml-spec7'
$env:HDC_DEVICE=$Device
$runArgs=@('workflow/verification/run_verified_round.py','--round',$RoundName,'--expected-source-sha256',$ExpectedSourceSha256,'--device',$Device,'--mode',$Mode)
if ($VisualReview) { $runArgs+=@('--visual-review',$VisualReview) }
if ($BuiltManifest) { $runArgs+=@('--built-manifest',$BuiltManifest) }
if ($InitialRotation -ne '') { $runArgs+=@('--initial-rotation',$InitialRotation) }
$runArgs+=@('--suite-kind',$SuiteKind)
if ($AllowRotation) { $runArgs+='--allow-rotation' }
& 'D:/HCUP/common/.venv/Scripts/python.exe' @runArgs
exit $LASTEXITCODE
