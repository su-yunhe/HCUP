$ErrorActionPreference = 'Stop'
if (Test-Path 'D:/hongmengcup/Enter-HarmonyEnv.ps1') {
  . 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
}
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'

$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $taskRoot
$taskLogs = Join-Path $taskRoot 'logs'
$taskRaw = Join-Path $taskLogs 'verification-do-prepare-r1.log'
$taskRecords = [System.Collections.Generic.List[object]]::new()
New-Item -ItemType Directory -Force -Path $taskLogs | Out-Null
Set-Content -LiteralPath $taskRaw -Value '' -Encoding utf8

function Invoke-TaskReadOnly {
  param([string]$Command, [string[]]$CommandArguments)
  $taskStart = Get-Date -Format o
  $taskOutput = @(& $Command @CommandArguments 2>&1 | ForEach-Object { $_.ToString() })
  $taskExit = $LASTEXITCODE
  $taskFinish = Get-Date -Format o
  $taskRecords.Add([pscustomobject]@{
    Command=$Command; Arguments=$CommandArguments; Cwd=$taskRoot
    Started=$taskStart; Finished=$taskFinish; ExitCode=$taskExit; Output=$taskOutput
  })
  Add-Content -LiteralPath $taskRaw -Value (($taskOutput -join "`n") + "`n") -Encoding utf8
  if ($taskExit -ne 0) { throw "Read-only command exited ${taskExit}: $Command" }
  return $taskOutput
}

$taskHead = Invoke-TaskReadOnly 'git' @('rev-parse','HEAD')
$taskStatus = Invoke-TaskReadOnly 'git' @('status','--short')
$taskTracked = Invoke-TaskReadOnly 'git' @('ls-files','--cached')
$taskNew = Invoke-TaskReadOnly 'git' @('ls-files','--others','--exclude-standard','--','entry','core','feature','hvigor')
$taskTargets = Invoke-TaskReadOnly 'hdc' @('list','targets')
$taskPython = (Resolve-Path -LiteralPath '../common/.venv/Scripts/python.exe').Path
$taskPythonInfo = Invoke-TaskReadOnly $taskPython @('-c','import sys, importlib.metadata as m; print(sys.executable); print(sys.version); print("hypium=" + m.version("hypium"))')

$taskManifest = foreach ($taskPath in (@($taskTracked) + @($taskNew) | Sort-Object -Unique)) {
  if ($taskPath -match '(^|/)(build|oh_modules|\.hvigor)/') { continue }
  $taskAbsolute = Join-Path $taskRoot $taskPath
  if (-not (Test-Path -LiteralPath $taskAbsolute -PathType Leaf)) { continue }
  $taskInfo = Get-Item -LiteralPath $taskAbsolute
  [pscustomobject]@{
    Path=$taskPath; Length=$taskInfo.Length
    SHA256=(Get-FileHash -Algorithm SHA256 -LiteralPath $taskAbsolute).Hash.ToLowerInvariant()
    Origin=$(if ($taskTracked -contains $taskPath) {'tracked'} else {'new-production-input'})
  }
}
$taskManifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'source-manifest-prepare.json') -Encoding utf8

$taskInputs = @('spec/requirement.md','spec/metadata.json','spec/acceptance.md','spec/baseline-notes.md','../common/test-harness/README.md','../common/test-harness/harness/driver.py','../common/test-harness/harness/runner.py','../common/test-harness/harness/report.py')
$taskHashes = foreach ($taskInput in $taskInputs) {
  [pscustomobject]@{Path=$taskInput;SHA256=(Get-FileHash -Algorithm SHA256 -LiteralPath $taskInput).Hash.ToLowerInvariant()}
}
$taskResult = [pscustomobject]@{
  Phase='prepare-only; no source freeze and no functional pass evidence'
  Recorded=(Get-Date -Format o); Cwd=$taskRoot; Head=($taskHead -join '')
  ManifestCount=@($taskManifest).Count; Status=$taskStatus; InputHashes=$taskHashes
  ToolPaths=@('git','hdc','hvigorw','node','java' | ForEach-Object {
    $taskTool=Get-Command $_ -ErrorAction SilentlyContinue
    [pscustomobject]@{Name=$_;Path=$taskTool.Source}
  })
  SessionId=$env:CODEX_SESSION_ID
  ThreadIdCandidate=$env:CODEX_THREAD_ID
  SessionIdentityNote='SessionId is inherited parent; ThreadIdCandidate requires parent verification, not independently confirmed.'
  Targets=$taskTargets; Python=$taskPythonInfo; Commands=$taskRecords
}
$taskResult | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $taskLogs 'verification-do-prepare-r1.json') -Encoding utf8
[pscustomobject]@{Recorded=$taskResult.Recorded;ManifestCount=$taskResult.ManifestCount;Head=$taskResult.Head;Targets=$taskTargets;Log='logs/verification-do-prepare-r1.json'} | ConvertTo-Json -Compress
