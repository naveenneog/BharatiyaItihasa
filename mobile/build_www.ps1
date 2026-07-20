# Assemble a minimal www/ for the Capacitor build. The app itself is loaded from the CDN
# (server.url in capacitor.config.json = https://indian-history.web.app), so www/ only needs a
# lightweight offline fallback page.
$ErrorActionPreference = "Stop"
$mobile = $PSScriptRoot
$www = Join-Path $mobile "www"
Remove-Item $www -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $www | Out-Null

@'
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Bharatiya Itihasa</title>
<style>html,body{margin:0;height:100%;background:#0d0b09;color:#e8b64a;
font-family:system-ui,sans-serif;display:grid;place-items:center;text-align:center}
a{color:#f0c15a}</style></head>
<body><div>
<h1>Bharatiya Itihasa</h1>
<p>Loading India&rsquo;s history&hellip;<br>You appear to be offline.</p>
<p><a href="https://indian-history.web.app">Open indian-history.web.app</a></p>
</div></body></html>
'@ | Set-Content -Encoding UTF8 (Join-Path $www "index.html")

Write-Host "www/ assembled (offline fallback; app loads from https://indian-history.web.app)"
