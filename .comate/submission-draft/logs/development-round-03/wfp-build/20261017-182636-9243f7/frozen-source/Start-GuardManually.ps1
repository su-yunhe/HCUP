#Requires -RunAsAdministrator
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][int]$TargetPid,
    [Parameter(Mandatory = $true)][string]$TargetStartUtc,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-f0-9]{64}$')][string]$TargetSha256,
    [Parameter(Mandatory = $true)][string]$InstanceRoot,
    [Parameter(Mandatory = $true)][string]$RunDirectory,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-f0-9]{32}$')][string]$RunNonce,
    [ValidateRange(30, 1800)][int]$MaxSeconds = 1200,
    [ValidateRange(5, 900)][int]$MaxBlockSeconds = 600
)
$ErrorActionPreference = 'Stop'
$binaryDirectory = Join-Path $PSScriptRoot 'bin'
$manifest = Get-Content -LiteralPath (Join-Path $binaryDirectory 'build-manifest.json') -Raw | ConvertFrom-Json
$executable = Join-Path $binaryDirectory 'VgSpec1WfpGuard.exe'
if ((Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.executableSha256) {
    throw 'The executable does not match the reviewed build manifest.'
}
foreach ($source in $manifest.sources) {
    $path = Join-Path $PSScriptRoot $source.name
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $source.sha256) {
        throw "Source changed since compilation: $($source.name)"
    }
}
# User manually starts this script in an already elevated console. No RunAs/UAC call.
# Explicit serve still starts unblocked and waits for a valid nonce-bound request.
& $executable --serve --target-pid $TargetPid --target-start-utc $TargetStartUtc --target-sha256 $TargetSha256 `
    --instance-root $InstanceRoot --run-dir $RunDirectory --nonce $RunNonce `
    --max-seconds $MaxSeconds --max-block-seconds $MaxBlockSeconds
exit $LASTEXITCODE
