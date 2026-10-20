. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
. D:/HCUP/vg-spec14/logs/do-validation/device-helpers.ps1
$completedRun = Get-Content -LiteralPath 'D:/HCUP/vg-spec14/logs/do-validation/runner-v11.json' -Raw | ConvertFrom-Json
if ($completedRun.cases.Count -ne 1 -or $completedRun.cases[0].outcome -ne 'pass') { throw 'Wait until final required method passes before cleanup.' }
$ownedPortMap = Get-Content -LiteralPath 'D:/HCUP/vg-spec14/logs/do-validation/owned-hypium-ports.json' -Raw | ConvertFrom-Json
$ownedPortNumbers = @($ownedPortMap.PSObject.Properties | ForEach-Object { $_.Value } | ForEach-Object { [string]$_ })
$inventory = @(Invoke-Vg14Hdc @('fport','ls'))
$removed = @()
foreach ($line in $inventory) {
  $parts = ([string]$line).Trim() -split '\s+'
  if ($parts.Count -ge 3 -and $parts[0] -eq '127.0.0.1:5555') {
    $portNumber = $parts[1] -replace '^tcp:', ''
    $isFixture = $parts[1] -eq 'tcp:18164' -and $parts[2] -eq 'tcp:18164'
    $isOwnedHypium = $parts[1] -match '^tcp:\d+$' -and $ownedPortNumbers -contains $portNumber -and $parts[2] -eq 'tcp:8012'
    if ($isFixture -or $isOwnedHypium) {
      Invoke-Vg14Hdc @('fport','rm',$parts[1],$parts[2]) | Out-Null
      $removed += [ordered]@{local=$parts[1];remote=$parts[2];kind=($(if ($isFixture) {'fixture'} else {'this-agent Hypium'}))}
    }
  }
}
$remaining = @(Invoke-Vg14Hdc @('fport','ls'))
$remaining | Set-Content -Encoding utf8 'D:/HCUP/vg-spec14/logs/do-validation/forward-inventory-after-cleanup.txt'
$serverRecords = @(Get-Content -LiteralPath 'D:/HCUP/vg-spec14/logs/do-validation/device-run-v11/server.jsonl' | ForEach-Object { $_ | ConvertFrom-Json })
$listeners = @(Get-NetTCPConnection -LocalPort 18164 -State Listen -ErrorAction SilentlyContinue)
$ownForwardRemains = $false
foreach ($line in $remaining) {
  $parts = ([string]$line).Trim() -split '\s+'
  if ($parts.Count -ge 3 -and $parts[0] -eq '127.0.0.1:5555' -and ($parts[1] -eq 'tcp:18164' -or $ownedPortNumbers -contains ($parts[1] -replace '^tcp:',''))) { $ownForwardRemains = $true }
}
[ordered]@{utc=(Get-Date -Format o);fixture_stopped=($listeners.Count -eq 0 -and @($serverRecords | Where-Object event -eq 'stopped').Count -gt 0);own_forwards_removed=(-not $ownForwardRemains);removed=$removed;remaining=$remaining;emulator_preserved=$true;device_temp_evidence_retained=$true;production_changed=$false} | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 'D:/HCUP/vg-spec14/logs/do-validation/cleanup.json'
Get-Content -LiteralPath 'D:/HCUP/vg-spec14/logs/do-validation/cleanup.json'
