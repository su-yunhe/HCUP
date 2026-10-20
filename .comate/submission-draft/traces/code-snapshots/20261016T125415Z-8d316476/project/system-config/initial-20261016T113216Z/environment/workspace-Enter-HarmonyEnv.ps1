$ErrorActionPreference = 'Stop'
. 'D:\hongmengcup\Enter-HarmonyEnv.ps1'

$env:HARMONY_WORKSPACE_HOME = Split-Path -Parent $PSScriptRoot
$env:HARMONY_PACKAGE_HOME = 'D:\SWE-OpenHarmony'
$env:VIRTUAL_ENV = Join-Path $env:HARMONY_WORKSPACE_HOME 'common\.venv'
$env:PIP_CONSTRAINT = 'D:\HarmonyDev\python-constraints.txt'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$taskHarnessPath = Join-Path $env:HARMONY_WORKSPACE_HOME 'common\test-harness'
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = $taskHarnessPath + ';' + $env:PYTHONPATH
} else {
    $env:PYTHONPATH = $taskHarnessPath
}
$env:Path = (Join-Path $env:VIRTUAL_ENV 'Scripts') + ';D:\Program Files\Git\bin;' + $env:Path
Write-Host "Workspace: $env:HARMONY_WORKSPACE_HOME"
Write-Host "Official package: $env:HARMONY_PACKAGE_HOME"
