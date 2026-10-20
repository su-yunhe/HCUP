$ErrorActionPreference = 'Continue'
. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location -LiteralPath 'D:/HCUP/vg-spec7'
$buildEvidence = 'traces/do-verification-build-v1'
New-Item -ItemType Directory -Path $buildEvidence -Force | Out-Null
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Get-Location).Path
$expectedHashes = @{
  'entry/src/main/ets/pages/settings/SettingsSyncSection.ets' = '1efbcd13f3c90a65144d0211edfe2db31daa8b33d03ca201cdd3e42802429fab'
  'entry/src/main/ets/pages/settings/SettingsSyncCards.ets' = '95aa35a51b0ff78397d8c036885b7a079d24160f06e94dabb57d3f78ff2bfeef'
}
foreach ($item in $expectedHashes.GetEnumerator()) {
  if ((Get-FileHash -LiteralPath $item.Key -Algorithm SHA256).Hash.ToLower() -ne $item.Value) {
    throw "Handoff source fingerprint changed: $($item.Key)"
  }
}
$envRecord = [ordered]@{
  time = (Get-Date -Format o)
  head = (git rev-parse HEAD)
  shell = $PSVersionTable.PSVersion.ToString()
  hvigorw = (Get-Command hvigorw).Source
  hdc = (Get-Command hdc).Source
  sdk = $env:DEVECO_SDK_HOME
  node = (node --version)
  java = ((java -version 2>&1) | Out-String)
  spec_sha256 = (Get-FileHash -LiteralPath spec/requirement.md -Algorithm SHA256).Hash.ToLower()
}
$envRecord | ConvertTo-Json -Depth 5 | Set-Content "$buildEvidence/environment.json" -Encoding utf8
@'
from hypium_tests.do_support import source_fingerprint
import json
from pathlib import Path
result=source_fingerprint()
Path('traces/do-verification-build-v1/source-before.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('fingerprinted production files:',len(result))
'@ | & '../common/.venv/Scripts/python.exe' -
if ($LASTEXITCODE -ne 0) { throw 'Source fingerprint failed' }
git status --short | Set-Content "$buildEvidence/status-before.txt" -Encoding utf8
$invocation = [ordered]@{start=(Get-Date -Format o); cwd=(Get-Location).Path; command='hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon'}
& hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | Tee-Object -FilePath "$buildEvidence/build.log"
$buildExit = $LASTEXITCODE
$invocation.end = Get-Date -Format o
$invocation.exit_code = $buildExit
$invocation | ConvertTo-Json -Depth 5 | Set-Content "$buildEvidence/invocation.json" -Encoding utf8
$buildExit | Set-Content "$buildEvidence/exit-code.txt"
@'
from hypium_tests.do_support import source_fingerprint
import json
from pathlib import Path
before=json.loads(Path('traces/do-verification-build-v1/source-before.json').read_text(encoding='utf-8'))
after=source_fingerprint()
root=Path('traces/do-verification-build-v1')
(root/'source-after.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
changes=sorted(k for k in before.keys()|after.keys() if before.get(k)!=after.get(k))
(root/'source-build-changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print('production fingerprint changes during clean build:',changes)
'@ | & '../common/.venv/Scripts/python.exe' -
git status --short | Set-Content "$buildEvidence/status-after.txt" -Encoding utf8
$hapPath = 'entry/build/default/outputs/default/entry-default-unsigned.hap'
if (Test-Path -LiteralPath $hapPath) {
  [ordered]@{path=(Resolve-Path $hapPath).Path;bytes=(Get-Item $hapPath).Length;sha256=(Get-FileHash $hapPath -Algorithm SHA256).Hash.ToLower()} | ConvertTo-Json | Set-Content "$buildEvidence/hap.json" -Encoding utf8
}
exit $buildExit
