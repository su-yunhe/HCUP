$ErrorActionPreference = 'Stop'

$devRoot = 'D:\HarmonyDev'
$studioRoot = Join-Path $devRoot 'DevEcoStudio-6.1.0'
$pythonEnv = 'D:\hongmengcup\SWE-OpenHarmony\.venv'

foreach ($directory in @('temp', 'cache\pip', 'cache\npm', 'cache\hvigor', 'logs')) {
    New-Item -ItemType Directory -Path (Join-Path $devRoot $directory) -Force | Out-Null
}

# These settings apply only to this PowerShell process and programs it starts.
$env:TEMP = Join-Path $devRoot 'temp'
$env:TMP = $env:TEMP
$env:PIP_CACHE_DIR = Join-Path $devRoot 'cache\pip'
$env:npm_config_cache = Join-Path $devRoot 'cache\npm'
$env:HVIGOR_USER_HOME = Join-Path $devRoot 'cache\hvigor'
$env:VIRTUAL_ENV = $pythonEnv
$env:DEVECO_STUDIO_HOME = $studioRoot
$env:DEVECOSTUDIO_PROPERTIES = Join-Path $devRoot 'config\deveco610.properties'

$toolPaths = @((Join-Path $pythonEnv 'Scripts'))
if (Test-Path -LiteralPath (Join-Path $studioRoot 'jbr\bin\java.exe')) {
    $env:JAVA_HOME = Join-Path $studioRoot 'jbr'
    $env:NODE_HOME = Join-Path $studioRoot 'tools\node'
    $env:DEVECO_SDK_HOME = Join-Path $studioRoot 'sdk'
    $competitionSdkRoot = Join-Path $devRoot 'sdk\api23'
    $competitionSdkMetadata = Join-Path $competitionSdkRoot 'default\sdk-pkg.json'
    if (Test-Path -LiteralPath $competitionSdkMetadata) {
        $competitionSdkInfo = Get-Content -LiteralPath $competitionSdkMetadata -Raw | ConvertFrom-Json
        if ($competitionSdkInfo.data.apiVersion -eq '23') {
            $env:DEVECO_SDK_HOME = $competitionSdkRoot
        }
    }
    $activeSdkInfo = Get-Content -LiteralPath (Join-Path $env:DEVECO_SDK_HOME 'default\sdk-pkg.json') -Raw | ConvertFrom-Json
    if ($activeSdkInfo.data.apiVersion -ne '23') {
        Write-Warning "Active SDK API is $($activeSdkInfo.data.apiVersion). Competition SDK API 23 is still pending."
    }
    $toolPaths += @(
        (Join-Path $studioRoot 'jbr\bin'),
        (Join-Path $studioRoot 'tools\node'),
        (Join-Path $studioRoot 'tools\ohpm\bin'),
        (Join-Path $studioRoot 'tools\hvigor\bin'),
        (Join-Path $studioRoot 'tools\emulator'),
        (Join-Path $env:DEVECO_SDK_HOME 'default\openharmony\toolchains'),
        (Join-Path $env:DEVECO_SDK_HOME 'default\hms\toolchains')
    )
} else {
    Write-Warning "DevEco Studio is not installed at $studioRoot yet."
}

$existingPaths = $toolPaths | Where-Object { Test-Path -LiteralPath $_ }
$env:Path = ($existingPaths -join ';') + ';' + $env:Path
Write-Host 'Harmony development environment loaded for this terminal.'
Write-Host "Python: $pythonEnv\Scripts\python.exe"
Write-Host "DevEco Studio: $studioRoot (6.1.0.860 / API 23)"
Write-Host "Downloads, temporary files and development caches: $devRoot"
