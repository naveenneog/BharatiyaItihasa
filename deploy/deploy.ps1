# Build dist/ (ONLY the QA-approved stories in deploy/approved.json) and deploy to the Firebase
# Hosting site "indian-history"  ->  https://indian-history.web.app  (Google's global CDN).
#
#   pwsh deploy/deploy.ps1
#
# One-time: `firebase login`, and the site is auto-created here if missing. Auth falls back to
# Google Application Default Credentials (gcloud auth application-default login).
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

$firebase = (Get-Command firebase -ErrorAction SilentlyContinue).Source
if (-not $firebase) { $firebase = Join-Path $env:APPDATA "npm\firebase.cmd" }
if (-not (Test-Path $firebase)) { throw "firebase CLI not found - run: npm i -g firebase-tools" }

$adc = Join-Path $env:APPDATA "gcloud\application_default_credentials.json"
if (-not $env:GOOGLE_APPLICATION_CREDENTIALS -and (Test-Path $adc)) {
  $env:GOOGLE_APPLICATION_CREDENTIALS = $adc
}

# 1) assemble dist/ (approved stories only, art -> webp)
python (Join-Path $root "tools\publish.py")

Push-Location $root
try {
  # 2) ensure the hosting site exists (no-op if it already does)
  & $firebase hosting:sites:create indian-history --project api-naveen 2>$null
  # 3) deploy just this site
  & $firebase deploy --only hosting --project api-naveen
} finally { Pop-Location }

Write-Host "`nDeployed. Live: https://indian-history.web.app"
