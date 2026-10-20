$script:DeviceKey = '127.0.0.1:5555'
$script:EvidenceRoot = 'D:\HCUP\vg-spec14\logs\analysis-baseline'
function Invoke-Device {
  param([string[]]$DeviceArgs)
  $record = [ordered]@{ time=(Get-Date -Format o); command='hdc -t ' + $script:DeviceKey + ' ' + ($DeviceArgs -join ' ') }
  $result = & hdc -t $script:DeviceKey @DeviceArgs 2>&1
  $record.exitCode = $LASTEXITCODE
  $record.output = ($result | Out-String)
  $record | ConvertTo-Json -Compress | Add-Content -Encoding utf8 (Join-Path $script:EvidenceRoot 'device-commands.jsonl')
  $result
}
function Get-UiNodes {
  param($Node)
  if ($Node.attributes) { $Node.attributes }
  foreach ($child in $Node.children) { Get-UiNodes $child }
}
function Capture-Ui {
  param([string]$Name, [switch]$Screenshot)
  Invoke-Device @('shell','uitest','dumpLayout','-p',('/data/local/tmp/vg14-' + $Name + '.json')) | Out-Null
  Invoke-Device @('file','recv',('/data/local/tmp/vg14-' + $Name + '.json'),(Join-Path $script:EvidenceRoot ('ui-' + $Name + '.json'))) | Out-Null
  if ($Screenshot) {
    Invoke-Device @('shell','snapshot_display','-f',('/data/local/tmp/vg14-' + $Name + '.jpeg')) | Out-Null
    Invoke-Device @('file','recv',('/data/local/tmp/vg14-' + $Name + '.jpeg'),(Join-Path $script:EvidenceRoot ('screen-' + $Name + '.jpeg'))) | Out-Null
  }
  $root = Get-Content (Join-Path $script:EvidenceRoot ('ui-' + $Name + '.json')) -Raw | ConvertFrom-Json
  $nodes = @(Get-UiNodes $root)
  $nodes | Where-Object { $_.text -or $_.type -match 'Input|Toggle|Loading|Button' -or $_.clickable -eq 'true' } | Select-Object text,type,id,bounds,enabled,visible,clickable,hint | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $script:EvidenceRoot ('ui-' + $Name + '-summary.json'))
  $nodes | Where-Object { $_.text -or $_.type -match 'Input|Toggle|Loading|Button' -or $_.clickable -eq 'true' } | Select-Object text,type,id,bounds,enabled,hint | Format-Table -AutoSize
}
