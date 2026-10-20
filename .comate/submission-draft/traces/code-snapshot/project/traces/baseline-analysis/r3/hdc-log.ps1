function Invoke-R3Hdc {
  param([string]$Label,[string[]]$Arguments)
  $r3Command = 'hdc '+($Arguments -join ' ')
  $r3Start = (Get-Date).ToUniversalTime().ToString('o')
  $r3Output = @(& hdc @Arguments 2>&1)
  $r3Code = $LASTEXITCODE
  $r3Output | Set-Content -Encoding utf8 ("logs/analysis-baseline-r3-"+$Label+".log")
  [pscustomobject]@{label=$Label;utc=$r3Start;command=$r3Command;exit_code=$r3Code;output=@($r3Output | ForEach-Object { $_.ToString() })} | ConvertTo-Json -Depth 6 | Tee-Object ("logs/analysis-baseline-r3-"+$Label+".json")
}
