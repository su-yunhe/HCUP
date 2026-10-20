param([Parameter(Mandatory=$true)][string]$RunId,[string]$CaseName='test_05_bidirectional_and_endpoint_policies',[Parameter(Mandatory=$true)][string]$Reason)
$ErrorActionPreference='Stop'
if (Test-Path 'D:/hongmengcup/Enter-HarmonyEnv.ps1') { . 'D:/hongmengcup/Enter-HarmonyEnv.ps1' }
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$taskRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $taskRoot
$taskCasePath=Join-Path $PSScriptRoot "$RunId/$CaseName"
$taskCapture=Get-ChildItem -LiteralPath $taskCasePath -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'capture-raw.log') } | Sort-Object Name | Select-Object -Last 1
$taskWaitEnd=(Get-Date).AddSeconds(40)
while ($taskCapture -and -not (Test-Path -LiteralPath (Join-Path $taskCapture.FullName 'action-and-engine.json')) -and (Get-Date) -lt $taskWaitEnd) { Start-Sleep -Milliseconds 200 }
if ($taskCapture -and -not (Test-Path -LiteralPath (Join-Path $taskCapture.FullName 'action-and-engine.json'))) { throw 'Current action evidence not saved; leave runner active.' }
$taskPattern="*harness.runner*--project D:\HCUP\cml-spec1*--json D:\HCUP\cml-spec1\logs\selftest-$RunId.json*"
$taskRunner=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -like $taskPattern -and $_.ExecutablePath -eq 'D:\Program Files\Python312\python.exe' })
if ($taskRunner.Count -ne 1) { throw 'Cannot uniquely identify this task runner; leave processes unchanged.' }
$taskRecord=[pscustomobject]@{ProcessId=$taskRunner[0].ProcessId;CommandLine=$taskRunner[0].CommandLine;Reason=$Reason;CompleteAction=$taskCapture.Name;Recorded=(Get-Date -Format o)}
$taskRecord | ConvertTo-Json | Set-Content -LiteralPath "logs/selftest-$RunId-interrupted.json" -Encoding utf8
Stop-Process -Id $taskRunner[0].ProcessId
$taskRecord | ConvertTo-Json
