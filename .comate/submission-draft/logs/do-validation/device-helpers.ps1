. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
$script:Vg14Device = '127.0.0.1:5555'
$script:Vg14Evidence = 'D:/HCUP/vg-spec14/logs/do-validation'
function Invoke-Vg14Hdc {
  param([string[]]$DeviceArgs)
  $record = [ordered]@{ utc=(Get-Date -Format o); argv=@('hdc','-t',$script:Vg14Device) + $DeviceArgs }
  $output = & hdc -t $script:Vg14Device @DeviceArgs 2>&1
  $record.exitCode = $LASTEXITCODE
  $record.output = ($output | Out-String)
  $record | ConvertTo-Json -Compress -Depth 5 | Add-Content -Encoding utf8 (Join-Path $script:Vg14Evidence 'device-commands.jsonl')
  if ($record.exitCode -ne 0 -or $record.output -match '(?i)\[fail\]|error:') { throw ('hdc failed: ' + $record.output) }
  $output
}
