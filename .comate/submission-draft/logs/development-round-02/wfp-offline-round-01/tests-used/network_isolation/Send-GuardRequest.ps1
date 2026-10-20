[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RunDirectory,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-f0-9]{32}$')][string]$RunNonce,
    [Parameter(Mandatory = $true)][ValidateRange(1, [long]::MaxValue)][long]$Sequence,
    [Parameter(Mandatory = $true)][ValidateSet('block', 'unblock', 'exit')][string]$Operation,
    [ValidateRange(1, 15)][int]$LeaseSeconds = 10
)
$ErrorActionPreference = 'Stop'
$resolvedDirectory = [IO.Path]::GetFullPath($RunDirectory).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
if (-not $resolvedDirectory.StartsWith('D:\HCUP\vg-spec1\logs\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Control directory must be inside this task logs directory.'
}
if (-not [IO.Directory]::Exists($resolvedDirectory)) { throw 'The reviewed run directory must already exist.' }
$currentPath = $resolvedDirectory
while ($currentPath) {
    if (([IO.File]::GetAttributes($currentPath) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse points are not accepted.' }
    $currentPath = [IO.Path]::GetDirectoryName($currentPath)
}
$created = [DateTime]::UtcNow
$request = [ordered]@{ nonce = $RunNonce; sequence = $Sequence; operation = $Operation;
    createdUtc = $created.ToString('o'); expiresUtc = $created.AddSeconds($LeaseSeconds).ToString('o') }
$text = $request | ConvertTo-Json -Compress
$path = Join-Path $resolvedDirectory 'request.json'
$temporary = Join-Path $resolvedDirectory ('request.' + [guid]::NewGuid().ToString('N') + '.tmp')
try {
    [IO.File]::WriteAllText($temporary, $text, [Text.UTF8Encoding]::new($false))
    if ([IO.File]::Exists($path)) {
        if (([IO.File]::GetAttributes($path) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Request cannot be a reparse point.' }
        [IO.File]::Replace($temporary, $path, $null)
    } else { [IO.File]::Move($temporary, $path) }
} finally {
    if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
}
Write-Output $text
