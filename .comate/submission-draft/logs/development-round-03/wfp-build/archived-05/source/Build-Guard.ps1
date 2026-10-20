[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'

$sourceNames = @('NativeWfp.cs', 'TargetGuard.cs', 'WfpSession.cs', 'RemovalObserver.cs', 'ControlProtocol.cs', 'SafetyWatchdog.cs', 'Program.cs')
$sourcePaths = @($sourceNames | ForEach-Object { Join-Path $PSScriptRoot $_ })
$compilerPath = 'C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe'
if (-not (Test-Path -LiteralPath $compilerPath)) { throw 'The installed x64 .NET Framework compiler is missing.' }
$outputDirectory = Join-Path $PSScriptRoot 'bin'
$logRoot = 'D:/HCUP/vg-spec1/logs/development-round-03/wfp-build'
$attempt = Join-Path $logRoot ((Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 6))
New-Item -ItemType Directory -Force -Path $outputDirectory, $attempt | Out-Null
$executable = Join-Path $outputDirectory 'VgSpec1WfpGuard.exe'
$compilerArguments = @('/nologo', '/target:exe', '/platform:x64', '/optimize+', '/checked+', '/warn:4', '/warnaserror+',
    '/reference:System.Management.dll', '/reference:System.Web.Extensions.dll', ('/out:' + $executable)) + $sourcePaths
& $compilerPath @compilerArguments 2>&1 | Tee-Object -FilePath (Join-Path $attempt 'compile.log')
$compilerExit = $LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $attempt 'compile-exit.txt'), [string]$compilerExit)
if ($compilerExit -ne 0) { throw "Compilation failed with exit code $compilerExit. See $attempt" }

# This mode is intentionally limited to layout/constants/path/hash/process reads.
& $executable --check 2>&1 | Tee-Object -FilePath (Join-Path $attempt 'check.json')
$checkExit = $LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $attempt 'check-exit.txt'), [string]$checkExit)
if ($checkExit -ne 0) { throw "Read-only --check failed with exit code $checkExit. See $attempt" }
$manifest = [ordered]@{
    schemaVersion = 1
    task = 'vg-spec1'
    builtAtUtc = [DateTime]::UtcNow.ToString('o')
    compiler = $compilerPath
    compilerVersion = (Get-Item -LiteralPath $compilerPath).VersionInfo.FileVersion
    executable = $executable
    executableSha256 = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    compileExit = $compilerExit
    checkExit = $checkExit
    logDirectory = $attempt
    sources = @($sourcePaths | ForEach-Object {
        [ordered]@{ name = [IO.Path]::GetFileName($_); sha256 = (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant() }
    })
}
$manifestJson = $manifest | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText((Join-Path $outputDirectory 'build-manifest.json'), $manifestJson, [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $attempt 'build-manifest.json'), $manifestJson, [Text.UTF8Encoding]::new($false))
$manifestJson
