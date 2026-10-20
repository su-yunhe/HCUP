$ErrorActionPreference = 'Stop'
$versionLog = $PSScriptRoot
$exe = 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/bin/VgSpec1WfpGuard.exe'
$identity = Get-Content -LiteralPath 'D:/HCUP/vg-spec1/logs/development-round-02/isolated-copy-preparation/target-identity.json' -Raw | ConvertFrom-Json
$instanceRoot = [IO.Path]::GetFullPath([string]$identity.instanceRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
$assembly = [Reflection.Assembly]::LoadFrom($exe)
$guardType = $assembly.GetType('VgSpec1.NetworkIsolation.TargetGuard', $true)
$flags = [Reflection.BindingFlags]::NonPublic -bor [Reflection.BindingFlags]::Static
$parse = $guardType.GetMethod('ParseCommandLine', $flags)
$validate = $guardType.GetMethod('ValidateCommandArguments', $flags)
$actual = (Get-Content -LiteralPath 'D:/HCUP/vg-spec1/logs/development-round-02/isolated-copy-preparation/process-after-start.json' -Raw | ConvertFrom-Json).CommandLine
$cases = @(
    @{ name='observed-official-command'; command=$actual; expected=$true },
    @{ name='duplicate-start-same-value'; command=($actual + ' -start VgSpec1ManualOffline'); expected=$false },
    @{ name='conflicting-start'; command=($actual + ' -start AnotherInstance'); expected=$false },
    @{ name='duplicate-port'; command=($actual + ' -hdcPort 11237'); expected=$false },
    @{ name='wrong-port'; command=$actual.Replace('-hdcPort 11237','-hdcPort 11238'); expected=$false },
    @{ name='compact-port'; command=$actual.Replace('-hdcPort 11237','-hdcPort11237'); expected=$false },
    @{ name='equals-port'; command=$actual.Replace('-hdcPort 11237','-hdcPort=11237'); expected=$false },
    @{ name='old-instance-alias'; command=$actual.Replace('-start VgSpec1ManualOffline','-instance VgSpec1ManualOffline'); expected=$false },
    @{ name='old-root-alias'; command=$actual.Replace('-instancePath ','-path '); expected=$false },
    @{ name='old-port-alias'; command=$actual.Replace('-hdcPort 11237','-hvdport 11237'); expected=$false },
    @{ name='instance-prefix-only'; command=$actual.Replace('-start VgSpec1ManualOffline','-start VgSpec1ManualOfflineOther'); expected=$false },
    @{ name='missing-port-value'; command=$actual.Replace('-hdcPort 11237','-hdcPort'); expected=$false },
    @{ name='unknown-option'; command=($actual + ' -unknown 123'); expected=$false },
    @{ name='wrong-image-root'; command=$actual.Replace('D:/HarmonyDev/emulator/images','D:/HarmonyDev/emulator/images-other'); expected=$false },
    @{ name='wrong-bootmode'; command=$actual.Replace('coldboot','hotboot'); expected=$false },
    @{ name='wrong-command-executable'; command=$actual.Replace('vg-spec1-isolated-emulator61','other-emulator'); expected=$false },
    @{ name='duplicate-root'; command=($actual + ' -instancePath ' + $identity.instanceRoot); expected=$false },
    @{ name='different-existing-instance-root'; command=$actual.Replace([string]$identity.instanceRoot,'D:/HCUP/vg-spec1/logs'); expected=$false }
)
$parserResults = @($cases | ForEach-Object {
    $case = $_
    $accepted = $false
    $reason = $null
    try {
        $parsed = [string[]]$parse.Invoke($null, [object[]]@([string]$case.command))
        $invocation = New-Object object[] 2
        $invocation[0] = $parsed
        $invocation[1] = $instanceRoot # Match the constructor's canonical root; do not weaken the guard.
        $validate.Invoke($null, $invocation) | Out-Null
        $accepted = $true
    } catch {
        $reason = $_.Exception.GetBaseException().Message
    }
    [ordered]@{ name=$case.name; accepted=$accepted; expectedAccepted=$case.expected; pass=($accepted -eq $case.expected); reason=$reason }
})
[IO.File]::WriteAllText((Join-Path $versionLog 'strict-parser-cases.json'), ($parserResults | ConvertTo-Json -Depth 5), [Text.UTF8Encoding]::new($false))
$parserResults | ConvertTo-Json -Depth 5
if (@($parserResults | Where-Object { -not $_.pass }).Count -gt 0) { throw 'Strict parser case failed.' }
