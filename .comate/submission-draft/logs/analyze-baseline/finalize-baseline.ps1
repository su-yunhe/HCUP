. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'D:/HCUP/vg-spec15'
$evidenceRoot = 'D:/HCUP/vg-spec15/logs/analyze-baseline'
$reference = Get-Content -LiteralPath 'workflow/analyze-code-fingerprint.json' -Raw | ConvertFrom-Json
$before = Get-Content -LiteralPath "$evidenceRoot/source-before.json" -Raw | ConvertFrom-Json
$after = [ordered]@{}
$changes = @()
foreach ($property in $reference.tracked_files_sha256.PSObject.Properties) {
  $actual = (Get-FileHash -LiteralPath $property.Name -Algorithm SHA256).Hash.ToLowerInvariant()
  $after[$property.Name] = $actual
  if ($actual -ne $property.Value -or $actual -ne $before.PSObject.Properties[$property.Name].Value) { $changes += $property.Name }
}
$after | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$evidenceRoot/source-after.json" -Encoding utf8
$listening = @(Get-NetTCPConnection -State Listen -LocalPort 18085 -ErrorAction SilentlyContinue)
$result = [ordered]@{
  time = (Get-Date).ToUniversalTime().ToString('o')
  head = (& git rev-parse HEAD)
  approved_head = $reference.head
  checked_tracked_files = $after.Count
  changed_since_approved_or_before = $changes
  spec_sha256 = (Get-FileHash -LiteralPath 'spec/requirement.md' -Algorithm SHA256).Hash.ToLowerInvariant()
  metadata_sha256 = (Get-FileHash -LiteralPath 'spec/metadata.json' -Algorithm SHA256).Hash.ToLowerInvariant()
  tracked_git_status = @(& git status --short --untracked-files=no)
  known_build_generated_paths = @('.hvigor/', 'entry/build/')
  known_test_generated_paths = @(@(Get-ChildItem -LiteralPath 'reports','tmp_hypium' -Recurse -File | ForEach-Object { [System.IO.Path]::GetRelativePath((Get-Location).Path, $_.FullName) }) + @('tmp_hypium/'))
  local_port_18085_listening = ($listening.Count -gt 0)
}
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$evidenceRoot/final-integrity.json" -Encoding utf8
Get-Content -LiteralPath "$evidenceRoot/final-integrity.json"
if ($changes.Count -gt 0 -or $result.head -ne $reference.head) { throw 'Fingerprint changed; affected evidence must be invalidated.' }
