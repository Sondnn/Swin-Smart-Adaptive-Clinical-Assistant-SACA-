param(
    [string]$Configuration = "Release",
    [string]$Runtime = "win-x64",
    [switch]$NoZip
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$projectFile = Join-Path $projectRoot "SACA.WindowsApp.csproj"
$publishRoot = Join-Path $projectRoot "publish"
$publishDir = Join-Path $publishRoot "SACA.WindowsApp-$Runtime"
$zipPath = Join-Path $publishRoot "SACA.WindowsApp-$Runtime.zip"

if (-not (Test-Path -LiteralPath $projectFile)) {
    throw "Project file not found: $projectFile"
}

New-Item -ItemType Directory -Force -Path $publishRoot | Out-Null

if (Test-Path -LiteralPath $publishDir) {
    $resolvedPublishDir = Resolve-Path -LiteralPath $publishDir
    $resolvedPublishRoot = Resolve-Path -LiteralPath $publishRoot

    if (-not $resolvedPublishDir.Path.StartsWith($resolvedPublishRoot.Path, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean an output path outside the publish folder: $resolvedPublishDir"
    }

    Remove-Item -LiteralPath $resolvedPublishDir.Path -Recurse -Force
}

dotnet publish $projectFile `
    --configuration $Configuration `
    --runtime $Runtime `
    --self-contained true `
    -p:PublishSingleFile=false `
    -p:PublishReadyToRun=false `
    --output $publishDir

if ($LASTEXITCODE -ne 0) {
    throw "dotnet publish failed with exit code $LASTEXITCODE"
}

if (-not $NoZip) {
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    $zipCreated = $false

    for ($attempt = 1; $attempt -le 3 -and -not $zipCreated; $attempt++) {
        try {
            Start-Sleep -Seconds 2
            Compress-Archive -Path (Join-Path $publishDir "*") -DestinationPath $zipPath -Force
            $zipCreated = $true
        }
        catch {
            if ($attempt -eq 3) {
                throw
            }
        }
    }
}

Write-Host ""
Write-Host "Demo app published to:"
Write-Host "  $publishDir"

if (-not $NoZip) {
    Write-Host ""
    Write-Host "Zip package created:"
    Write-Host "  $zipPath"
}
