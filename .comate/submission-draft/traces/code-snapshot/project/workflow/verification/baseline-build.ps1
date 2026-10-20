. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec7
Start-Transcript -LiteralPath D:/HCUP/cml-spec7/logs/analysis-baseline/build-full-transcript.txt -Force
Get-Date -Format o
Write-Output 'COMMAND: hvigorw --mode project -p product=default clean --no-daemon'
hvigorw --mode project -p product=default clean --no-daemon *>&1 | Tee-Object -FilePath logs/analysis-baseline/clean-raw.txt | Out-Host
$cleanExit = $LASTEXITCODE
Write-Output "CLEAN_EXIT_CODE=$cleanExit"
Write-Output 'COMMAND: hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental'
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental *>&1 | Tee-Object -FilePath logs/analysis-baseline/build-full-raw.txt | Out-Host
$buildExit = $LASTEXITCODE
Write-Output "BUILD_EXIT_CODE=$buildExit"
$haps = Get-ChildItem -LiteralPath entry/build -Recurse -File -Filter *.hap -ErrorAction SilentlyContinue
$haps | Select-Object FullName,Length,LastWriteTimeUtc
$haps | Get-FileHash -Algorithm SHA256 | Format-List | Out-Host
Get-Date -Format o
Stop-Transcript
exit $buildExit
