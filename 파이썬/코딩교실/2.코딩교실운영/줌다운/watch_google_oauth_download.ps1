$ErrorActionPreference = "Stop"

$targetDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetFile = Join-Path $targetDir "google_oauth_client.json"
$downloads = Join-Path $env:USERPROFILE "Downloads"
$logFile = Join-Path $targetDir "google_oauth_setup.log"
$startedAt = Get-Date
$deadline = $startedAt.AddMinutes(20)

function Write-SetupLog([string]$message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $logFile -Encoding UTF8 -Value "[$timestamp] $message"
}

function Test-GoogleOAuthClientJson([string]$path) {
    try {
        $json = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $false
    }

    if ($null -eq $json.installed) {
        return $false
    }

    $client = $json.installed
    return (
        -not [string]::IsNullOrWhiteSpace($client.client_id) -and
        -not [string]::IsNullOrWhiteSpace($client.client_secret) -and
        -not [string]::IsNullOrWhiteSpace($client.auth_uri) -and
        -not [string]::IsNullOrWhiteSpace($client.token_uri)
    )
}

Write-SetupLog "OAuth client JSON watcher started. Downloads=$downloads Target=$targetFile"

while ((Get-Date) -lt $deadline) {
    $candidates = Get-ChildItem -LiteralPath $downloads -Filter "*.json" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -ge $startedAt.AddMinutes(-1) } |
        Sort-Object LastWriteTime -Descending

    foreach ($candidate in $candidates) {
        if (Test-GoogleOAuthClientJson $candidate.FullName) {
            Copy-Item -LiteralPath $candidate.FullName -Destination $targetFile -Force
            Write-SetupLog "OAuth client JSON copied to target from downloaded file: $($candidate.Name)"
            exit 0
        }
    }

    Start-Sleep -Seconds 2
}

Write-SetupLog "OAuth client JSON watcher timed out."
exit 1
