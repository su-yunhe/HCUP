$ErrorActionPreference = 'Stop'
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location -LiteralPath D:/HCUP/vg-spec13
$buildLogRoot = 'D:/HCUP/vg-spec13/logs/implementation-build'
New-Item -ItemType Directory -Path $buildLogRoot -Force | Out-Null
$buildAttempt = Get-Date -Format 'yyyyMMdd-HHmmss'
$installLog = Join-Path $buildLogRoot ($buildAttempt + '-ohpm.log')
$compileLog = Join-Path $buildLogRoot ($buildAttempt + '-build.log')
$buildStartedAt = [DateTime]::UtcNow.ToString('o')
& ohpm install --all --registry https://ohpm.openharmony.cn/ohpm/ --strict_ssl true 2>&1 | Tee-Object -FilePath $installLog
$installCode = $LASTEXITCODE
if ($installCode -ne 0) {
  @{ started_at = $buildStartedAt; ohpm_exit_code = $installCode; ohpm_log = $installLog } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $buildLogRoot ($buildAttempt + '-result.json')) -Encoding utf8
  exit $installCode
}
& hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon 2>&1 | Tee-Object -FilePath $compileLog
$compileCode = $LASTEXITCODE
@{
  started_at = $buildStartedAt
  ended_at = [DateTime]::UtcNow.ToString('o')
  ohpm_exit_code = $installCode
  build_exit_code = $compileCode
  ohpm_log = $installLog
  build_log = $compileLog
  command = 'hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon'
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $buildLogRoot ($buildAttempt + '-result.json')) -Encoding utf8
exit $compileCode
