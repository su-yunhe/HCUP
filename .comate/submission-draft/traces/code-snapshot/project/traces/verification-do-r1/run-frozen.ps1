param(
  [Parameter(Mandatory=$true)][ValidateSet('Build','Install','Probe','Run')][string]$Phase,
  [switch]$FrozenAuthorized,
  [switch]$SkipClean,
  [string]$HapRecord = '',
  [string]$FrozenManifest = 'traces/do-implementation/source-frozen-r1.json',
  [string]$Handoff = 'workflow/implementation/do-handoff-r1.md',
  [string]$HandoffSHA256 = '65c65b492e42092f5e9cfc9adde99f32385e83cd96ab4a0df3f7766c59ec8c82',
  [string]$Device = '127.0.0.1:11245',
  [string]$RunId = 'run-r1'
)
$ErrorActionPreference = 'Stop'
if (-not $FrozenAuthorized) { throw 'This execution helper requires the parent Agent source-freeze authorization.' }
if ($Device -ne '127.0.0.1:11245') { throw 'This run is only authorized to use the question-owned 11245 device.' }
if (Test-Path 'D:/hongmengcup/Enter-HarmonyEnv.ps1') { . 'D:/hongmengcup/Enter-HarmonyEnv.ps1' }
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $taskRoot
$taskRecords = [System.Collections.Generic.List[object]]::new()
$taskPrefix = "verification-do-$($Phase.ToLower())-$RunId"
$taskResultPath = Join-Path $taskRoot "logs/$taskPrefix-commands.json"

function Invoke-TaskCommand {
  param([string]$Label,[string]$Command,[string[]]$CommandArguments)
  $taskStart = Get-Date -Format o
  $taskLog = Join-Path $taskRoot "logs/$taskPrefix-$Label.log"
  & $Command @CommandArguments 2>&1 | Tee-Object -FilePath $taskLog
  $taskExit = $LASTEXITCODE
  $taskRecords.Add([pscustomobject]@{Label=$Label;Command=$Command;Arguments=$CommandArguments;Cwd=(Get-Location).Path;Started=$taskStart;Finished=(Get-Date -Format o);ExitCode=$taskExit;RawLog=$taskLog})
  $taskRecords | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskResultPath -Encoding utf8
  if ($taskExit -ne 0) { throw "$Label exited $taskExit; see $taskLog" }
  if (Select-String -LiteralPath $taskLog -Pattern '^\[Fail\]|^error:' -Quiet) { throw "$Label reported a failure despite native exit 0; see $taskLog" }
}

function Assert-TaskFrozen {
  param([string]$Label)
  $taskFrozen = Get-Content -LiteralPath $FrozenManifest -Raw | ConvertFrom-Json
  $taskRows = foreach ($taskProperty in $taskFrozen.files_sha256.PSObject.Properties) {
    $taskActual = (Get-FileHash -Algorithm SHA256 -LiteralPath $taskProperty.Name).Hash.ToLowerInvariant()
    [pscustomobject]@{Path=$taskProperty.Name;Expected=$taskProperty.Value;Actual=$taskActual;Same=($taskActual -eq $taskProperty.Value)}
  }
  $taskRows | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot "$RunId-$Label-source.json") -Encoding utf8
  $taskChanges = @($taskRows | Where-Object { -not $_.Same })
  if ($taskChanges.Count -gt 0) { throw "Frozen source changed: $($taskChanges.Path -join ', ')" }
}

$taskApprovedHashes = @{
  'spec/requirement.md'='491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b'
  'spec/acceptance.md'='7d7cedd00fb2c8cd5ce5be285da8428477a29ea1228cf63d0f8c9ec371b8497a'
}
$taskApprovedHashes[$Handoff] = $HandoffSHA256
foreach ($taskInput in $taskApprovedHashes.Keys) {
  if ((Get-FileHash -Algorithm SHA256 -LiteralPath $taskInput).Hash.ToLowerInvariant() -ne $taskApprovedHashes[$taskInput]) { throw "Approved input changed: $taskInput" }
}
Assert-TaskFrozen 'before'
$taskHap = Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
$taskHapRecord = $(if ($HapRecord) { Join-Path $taskRoot $HapRecord } else { Join-Path $PSScriptRoot "independent-hap-$RunId.json" })

if ($Phase -eq 'Build') {
  Invoke-TaskCommand 'node-version' 'node' @('--version')
  Invoke-TaskCommand 'java-version' 'java' @('-version')
  Invoke-TaskCommand 'hdc-version' 'hdc' @('-v')
  if (-not $SkipClean) { Invoke-TaskCommand 'clean' 'hvigorw' @('clean','--mode','module','-p','product=default','-p','buildMode=debug','--no-daemon') }
  Invoke-TaskCommand 'assembleHap' 'hvigorw' @('assembleHap','--mode','module','-p','product=default','-p','buildMode=debug','--no-daemon')
  $taskHapInfo = Get-Item -LiteralPath $taskHap
  [pscustomobject]@{Path=$taskHap;Length=$taskHapInfo.Length;SHA256=(Get-FileHash -Algorithm SHA256 -LiteralPath $taskHap).Hash.ToLowerInvariant();LastWrite=$taskHapInfo.LastWriteTime.ToString('o');Recorded=(Get-Date -Format o);FrozenManifest=$FrozenManifest;Handoff=$Handoff} | ConvertTo-Json | Set-Content -LiteralPath $taskHapRecord -Encoding utf8
}
if ($Phase -in @('Install','Run')) {
  $taskHapInfo = Get-Content -LiteralPath $taskHapRecord -Raw | ConvertFrom-Json
  if ((Get-FileHash -Algorithm SHA256 -LiteralPath $taskHap).Hash.ToLowerInvariant() -ne $taskHapInfo.SHA256) { throw 'Current HAP differs from independently built package.' }
  Invoke-TaskCommand 'install-current-hap' 'hdc' @('-t',$Device,'install','-r',$taskHap)
  if (-not (Select-String -LiteralPath (Join-Path $taskRoot "logs/$taskPrefix-install-current-hap.log") -Pattern 'install bundle successfully' -Quiet)) { throw 'Installer did not confirm success.' }
  Invoke-TaskCommand 'installed-bundle' 'hdc' @('-t',$Device,'shell','bm','dump','-n','com.joker.coolmall')
}
if ($Phase -eq 'Probe') {
  Invoke-TaskCommand 'device-version' 'hdc' @('-t',$Device,'shell','param','get','const.product.software.version')
  Invoke-TaskCommand 'device-api' 'hdc' @('-t',$Device,'shell','param','get','const.ohos.apiversion')
  Invoke-TaskCommand 'start' 'hdc' @('-t',$Device,'shell','aa','start','-a','EntryAbility','-b','com.joker.coolmall')
  Start-Sleep -Milliseconds 600
  Invoke-TaskCommand 'first-tree' 'hdc' @('-t',$Device,'shell','uitest','dumpLayout','-a','-p','/data/local/tmp/cml_spec1_first.json')
  Invoke-TaskCommand 'first-tree-recv' 'hdc' @('-t',$Device,'file','recv','/data/local/tmp/cml_spec1_first.json',(Join-Path $PSScriptRoot 'first.json'))
  Invoke-TaskCommand 'first-screen' 'hdc' @('-t',$Device,'shell','uitest','screenCap','-p','/data/local/tmp/cml_spec1_first.png')
  Invoke-TaskCommand 'first-screen-recv' 'hdc' @('-t',$Device,'file','recv','/data/local/tmp/cml_spec1_first.png',(Join-Path $PSScriptRoot 'first.png'))
}
if ($Phase -eq 'Run') {
  $env:PYTHONPATH = (Resolve-Path -LiteralPath '../common/test-harness').Path
  $env:PYTHONDONTWRITEBYTECODE = '1'
  $env:CML_RUN_ID = $RunId
  $taskPython = (Resolve-Path -LiteralPath '../common/.venv/Scripts/python.exe').Path
  Push-Location -LiteralPath (Join-Path $taskRoot 'logs')
  try {
    Invoke-TaskCommand 'runner' $taskPython @('-m','harness.runner','--project',$taskRoot,'--device',$Device,'--json',(Join-Path $taskRoot "logs/selftest-$RunId.json"))
  } finally { Pop-Location }
}
Assert-TaskFrozen 'after'
