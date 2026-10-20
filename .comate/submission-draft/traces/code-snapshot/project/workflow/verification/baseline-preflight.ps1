. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec7
$recordPath = 'D:/HCUP/cml-spec7/logs/analysis-baseline/preflight.txt'
Start-Transcript -LiteralPath $recordPath -Force
Get-Date -Format o
Get-Item Env:CODEX_THREAD_ID,Env:CODEX_SESSION_ID,Env:DEVECO_SDK_HOME,Env:DEVECO_STUDIO_HOME
Get-Command hvigorw,hdc,python,node | Select-Object Name,Source
python workflow/verification/baseline-fingerprint.py fingerprint-before.json
Write-Output "fingerprint exit=$LASTEXITCODE"
hdc list targets
Write-Output "hdc list targets exit=$LASTEXITCODE"
hdc shell hidumper -s AbilityManagerService -a '-l'
Write-Output "foreground dump exit=$LASTEXITCODE"
hdc shell hidumper -s WindowManagerService -a '-a'
Write-Output "window dump exit=$LASTEXITCODE"
$env:PYTHONPATH='D:/HCUP/cml-spec7/test-harness'
$env:PYTHONDONTWRITEBYTECODE='1'
python -m harness.env_check
Write-Output "environment check exit=$LASTEXITCODE"
Stop-Transcript
