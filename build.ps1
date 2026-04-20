$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$distRoot = Join-Path $projectRoot "dist\\vote-batch"
$browserSourceRoot = Join-Path $env:LOCALAPPDATA "ms-playwright"
$browserTargetRoot = Join-Path $distRoot "ms-playwright"
$bundledAccountsSource = Join-Path $projectRoot "accounts.csv"
$bundledAccountsTarget = Join-Path $distRoot "accounts.csv"

python -m PyInstaller --noconfirm --clean --onedir --name vote-batch main.py

if (-not (Test-Path $bundledAccountsSource)) {
    throw "Bundled accounts CSV not found at $bundledAccountsSource"
}

Copy-Item -Path $bundledAccountsSource -Destination $bundledAccountsTarget -Force

if (-not (Test-Path $browserSourceRoot)) {
    throw "Playwright browser cache not found at $browserSourceRoot"
}

New-Item -ItemType Directory -Path $browserTargetRoot -Force | Out-Null

$patterns = @(
    "chromium-*",
    "chromium_headless_shell-*",
    "ffmpeg-*",
    "winldd-*"
)

foreach ($pattern in $patterns) {
    Get-ChildItem -Path $browserSourceRoot -Directory -Filter $pattern | ForEach-Object {
        $target = Join-Path $browserTargetRoot $_.Name
        Copy-Item -Path $_.FullName -Destination $target -Recurse -Force
    }
}
