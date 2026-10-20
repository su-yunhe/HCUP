$ErrorActionPreference = 'Stop'
$exe = 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/bin/VgSpec1WfpGuard.exe'
$assembly = [Reflection.Assembly]::LoadFrom($exe)
$type = $assembly.GetType('VgSpec1.NetworkIsolation.WfpSession', $true)
$method = $type.GetMethod('FlagsAllowed', [Reflection.BindingFlags]::NonPublic -bor [Reflection.BindingFlags]::Static)
$constantType = $assembly.GetType('VgSpec1.NetworkIsolation.NativeWfp', $true)
$indexed = $constantType.GetField('FilterIndexed', [Reflection.BindingFlags]::NonPublic -bor [Reflection.BindingFlags]::Static).GetRawConstantValue()
if ($indexed -ne 64) { throw 'INDEXED differs from the verified official header constant.' }
$samples = [Collections.Generic.List[uint32]]::new()
$samples.Add(0)
for ($bit = 0; $bit -lt 32; $bit++) { $samples.Add([uint32]([uint64]1 -shl $bit)) }
for ($bit = 0; $bit -lt 32; $bit++) {
    if ($bit -ne 6) { $samples.Add([uint32](([uint64]1 -shl $bit) -bor [uint64]64)) }
}
$samples.Add([uint32]::MaxValue)
$results = @(
    foreach ($flags in $samples) {
        foreach ($readback in @($false, $true)) {
            $expected = $flags -eq 0 -or ($readback -and $flags -eq 64)
            $actual = [bool]$method.Invoke($null, [object[]]@([uint32]$flags, [bool]$readback))
            [ordered]@{ flags=$flags; flagsHex=('0x{0:x8}' -f $flags); readback=$readback; expectedAllowed=$expected; actualAllowed=$actual; pass=($actual -eq $expected) }
        }
    }
)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'flags-policy-cases.json'), ($results | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
[ordered]@{ cases=$results.Count; failed=@($results | Where-Object { -not $_.pass }).Count; officialIndexed=$indexed; nativeWfpCalls=0 } | ConvertTo-Json
if (@($results | Where-Object { -not $_.pass }).Count -gt 0) { throw 'Flags policy mismatch.' }
