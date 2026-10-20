param([string]$Round = '02')
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'D:/HCUP/vg-spec15'
$evidenceRoot = "D:/HCUP/vg-spec15/logs/implementation-validation/build-round-$Round"
New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null
$env:VG15_AUDIT_DIR = $evidenceRoot
& D:/HCUP/common/.venv/Scripts/python.exe hypium_tests/audit.py source-before-build
$started = (Get-Date).ToUniversalTime().ToString('o')
& hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon *> "$evidenceRoot/build.raw.log"
$buildExit = $LASTEXITCODE
[ordered]@{ command='hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon'; started=$started; finished=(Get-Date).ToUniversalTime().ToString('o'); exit_code=$buildExit; node=(& node --version); sdk=$env:DEVECO_SDK_HOME; java=$env:JAVA_HOME } | ConvertTo-Json | Set-Content -LiteralPath "$evidenceRoot/build-result.json" -Encoding utf8
& D:/HCUP/common/.venv/Scripts/python.exe hypium_tests/audit.py source-after-build
& D:/HCUP/common/.venv/Scripts/python.exe hypium_tests/audit.py warnings
Get-ChildItem -LiteralPath entry/build/default/outputs/default -File | ForEach-Object { [ordered]@{ path=$_.FullName; length=$_.Length; modified_utc=$_.LastWriteTimeUtc.ToString('o'); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() } } | ConvertTo-Json | Set-Content -LiteralPath "$evidenceRoot/artifacts.json" -Encoding utf8
Get-Content -LiteralPath "$evidenceRoot/build-result.json"
Get-Content -LiteralPath "$evidenceRoot/build.raw.log" -Tail 14
Remove-Item Env:VG15_AUDIT_DIR
exit $buildExit
