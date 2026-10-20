. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location 'D:/HCUP/cml-spec1'
$buildSteps = @(@('clean','--mode','module','-p','product=default','-p','buildMode=debug','--no-daemon'),@('assembleHap','--mode','module','-p','product=default','-p','buildMode=debug','--no-daemon'))
$buildResults = @()
foreach ($buildStep in $buildSteps) {
  $buildLabel = $buildStep[0]
  $buildStart = (Get-Date).ToUniversalTime().ToString('o')
  & hvigorw @buildStep *>&1 | Tee-Object -FilePath "logs/analysis-baseline-$buildLabel.log"
  $buildCode = $LASTEXITCODE
  $buildResults += [pscustomobject]@{command=('hvigorw '+($buildStep -join ' '));exit_code=$buildCode;start_utc=$buildStart;end_utc=(Get-Date).ToUniversalTime().ToString('o');log="logs/analysis-baseline-$buildLabel.log"}
  $buildResults | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 'logs/analysis-baseline-build-results.json'
  if ($buildCode -ne 0) { exit $buildCode }
}
Get-ChildItem 'entry/build/default/outputs/default/*.hap' | ForEach-Object { $buildHash = Get-FileHash $_.FullName -Algorithm SHA256; [pscustomobject]@{path=$_.FullName;bytes=$_.Length;sha256=$buildHash.Hash.ToLowerInvariant();last_write_utc=$_.LastWriteTimeUtc.ToString('o')} } | ConvertTo-Json | Set-Content -Encoding utf8 'logs/analysis-baseline-hap.json'
