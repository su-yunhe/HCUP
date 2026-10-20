. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'D:/HCUP/vg-spec15'
$evidenceRoot = 'D:/HCUP/vg-spec15/logs/analyze-baseline'
$reference = Get-Content -LiteralPath 'workflow/analyze-code-fingerprint.json' -Raw | ConvertFrom-Json
$snapshot = [ordered]@{}
$mismatches = @()
foreach ($property in $reference.tracked_files_sha256.PSObject.Properties) {
  $actual = (Get-FileHash -LiteralPath $property.Name -Algorithm SHA256).Hash.ToLowerInvariant()
  $snapshot[$property.Name] = $actual
  if ($actual -ne $property.Value) { $mismatches += $property.Name }
}
$snapshot | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$evidenceRoot/source-before.json" -Encoding utf8
$preflight = [ordered]@{
  time = (Get-Date).ToUniversalTime().ToString('o')
  cwd = (Get-Location).Path
  thread_id = $env:CODEX_THREAD_ID
  head = (& git rev-parse HEAD)
  expected_head = $reference.head
  spec_sha256 = (Get-FileHash -LiteralPath 'spec/requirement.md' -Algorithm SHA256).Hash.ToLowerInvariant()
  metadata_sha256 = (Get-FileHash -LiteralPath 'spec/metadata.json' -Algorithm SHA256).Hash.ToLowerInvariant()
  fingerprint_mismatches = $mismatches
  powershell = $PSVersionTable.PSVersion.ToString()
  hvigorw = (Get-Command hvigorw.bat).Source
  node = (Get-Command node).Source
  node_version = (& node --version)
  hdc = (Get-Command hdc).Source
  hdc_version = (& hdc -v)
  sdk = $env:DEVECO_SDK_HOME
  java = $env:JAVA_HOME
  tracked_status = @(& git status --short --untracked-files=no)
}
$preflight | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$evidenceRoot/preflight.json" -Encoding utf8
if ($mismatches.Count -gt 0 -or $preflight.head -ne $reference.head) { throw 'Source fingerprint mismatch; build evidence invalid.' }
$command = 'hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon'
$started = (Get-Date).ToUniversalTime().ToString('o')
& hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon *> "$evidenceRoot/build.raw.log"
$buildExit = $LASTEXITCODE
[ordered]@{ command = $command; started = $started; finished = (Get-Date).ToUniversalTime().ToString('o'); exit_code = $buildExit } | ConvertTo-Json | Set-Content -LiteralPath "$evidenceRoot/build-result.json" -Encoding utf8
Get-ChildItem -LiteralPath 'entry/build/default/outputs/default' -File | ForEach-Object {
  [ordered]@{ path = $_.FullName; length = $_.Length; modified_utc = $_.LastWriteTimeUtc.ToString('o'); sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
} | ConvertTo-Json | Set-Content -LiteralPath "$evidenceRoot/artifacts.json" -Encoding utf8
Get-Content -LiteralPath "$evidenceRoot/build-result.json"
Get-Content -LiteralPath "$evidenceRoot/build.raw.log" -Tail 18
exit $buildExit
