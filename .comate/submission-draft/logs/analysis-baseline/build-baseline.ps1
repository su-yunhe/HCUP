. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec24
$ErrorActionPreference = 'Continue'
$taskLog = 'D:/HCUP/cml-spec24/logs/analysis-baseline'
$taskStart = Get-Date
& python "$taskLog/capture_fingerprint.py" fingerprint-before-build > "$taskLog/fingerprint-before-build-summary.log" 2>&1
$taskFingerprintExit = $LASTEXITCODE
if ($taskFingerprintExit -ne 0) { throw 'Approved source fingerprint mismatch; build cancelled.' }
$taskCommand = 'hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon'
& hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon *> "$taskLog/build-full.log"
$taskBuildExit = $LASTEXITCODE
& python "$taskLog/capture_fingerprint.py" fingerprint-after-build > "$taskLog/fingerprint-after-build-summary.log" 2>&1
$taskAfterExit = $LASTEXITCODE
$taskArtifacts = @(Get-ChildItem entry/build -Recurse -File -Filter *.hap | ForEach-Object { [ordered]@{path=$_.FullName;bytes=$_.Length;lastWriteUtc=$_.LastWriteTimeUtc.ToString('o');sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()} })
[ordered]@{
  startUtc=$taskStart.ToUniversalTime().ToString('o');endUtc=(Get-Date).ToUniversalTime().ToString('o');
  command=$taskCommand;cwd=(Get-Location).Path;buildExitCode=$taskBuildExit;
  fingerprintBeforeExitCode=$taskFingerprintExit;fingerprintAfterExitCode=$taskAfterExit;
  sdk=$env:DEVECO_SDK_HOME;studio=$env:DEVECO_STUDIO_HOME;java=$env:JAVA_HOME;
  hvigor=(Get-Command hvigorw.bat).Source;node=(Get-Command node.exe | Select-Object -First 1).Source;
  hdc=(Get-Command hdc.exe).Source;artifacts=$taskArtifacts
} | ConvertTo-Json -Depth 8 | Set-Content "$taskLog/build-result.json" -Encoding utf8
Get-Content "$taskLog/build-result.json"
Get-Content "$taskLog/build-full.log" -Tail 25
exit $taskBuildExit
