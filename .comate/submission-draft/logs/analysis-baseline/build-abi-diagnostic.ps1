. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
$ErrorActionPreference = 'Stop'
$taskLog = 'D:/HCUP/cml-spec24/logs/analysis-baseline'
Set-Location D:/HCUP/cml-spec24
& python "$taskLog/prepare_abi_diagnostic.py" *> "$taskLog/abi-diagnostic-prepare.log"
if ($LASTEXITCODE -ne 0) { Get-Content "$taskLog/abi-diagnostic-prepare.log"; throw 'Diagnostic preparation failed.' }
$taskLinks = Get-Content -Raw "$taskLog/abi-diagnostic-dependency-links.json" | ConvertFrom-Json
foreach ($taskLink in $taskLinks) {
  New-Item -ItemType Junction -Path $taskLink.link -Target $taskLink.target | Out-Null
}
& python "$taskLog/hash_dependencies.py" dependencies-before-diagnostic *> "$taskLog/dependencies-before-diagnostic.log"
$taskStart = Get-Date
Set-Location "$taskLog/abi-diagnostic"
$ErrorActionPreference = 'Continue'
& hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon *> "$taskLog/abi-diagnostic-build-full.log"
$taskBuildExit = $LASTEXITCODE
$taskArtifacts = @(Get-ChildItem entry/build -Recurse -File -Filter *.hap -ErrorAction SilentlyContinue | ForEach-Object { [ordered]@{path=$_.FullName;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()} })
Set-Location D:/HCUP/cml-spec24
& python "$taskLog/hash_dependencies.py" dependencies-after-diagnostic *> "$taskLog/dependencies-after-diagnostic.log"
& python "$taskLog/capture_fingerprint.py" fingerprint-after-abi-diagnostic *> "$taskLog/fingerprint-after-abi-diagnostic-summary.log"
$taskFingerprintExit=$LASTEXITCODE
[ordered]@{startUtc=$taskStart.ToUniversalTime().ToString('o');endUtc=(Get-Date).ToUniversalTime().ToString('o');cwd="$taskLog/abi-diagnostic";command='hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon';buildExitCode=$taskBuildExit;originalSourceFingerprintExitCode=$taskFingerprintExit;artifacts=$taskArtifacts;label='ABI adapted diagnostic build; not pristine baseline'} | ConvertTo-Json -Depth 7 | Set-Content "$taskLog/abi-diagnostic-build-result.json" -Encoding utf8
Get-Content "$taskLog/abi-diagnostic-preparation.json"
Get-Content "$taskLog/abi-diagnostic-build-result.json"
Get-Content "$taskLog/abi-diagnostic-build-full.log" -Tail 20
exit $taskBuildExit
