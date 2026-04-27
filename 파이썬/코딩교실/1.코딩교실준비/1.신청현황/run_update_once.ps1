$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Targets = @("pohang:1", "gumi:1")
$LogDir = Join-Path $Root "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = Join-Path $LogDir "update_$Timestamp.log"

function Get-PythonRunner {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{ Exe = "py"; PrefixArgs = @("-3") }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{ Exe = "python"; PrefixArgs = @() }
    }

    throw "Python was not found. Install Python 3.11+ and try again."
}

$ExitCode = 0
Start-Transcript -Path $LogFile -Append | Out-Null

try {
    Write-Host "=== Coding classroom update started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
    Write-Host "Project root: $Root"
    Write-Host "Targets: $($Targets -join ', ')"

    $Runner = Get-PythonRunner
    $MainScript = Join-Path $Root "_sincheong\신청현황확인.py"
    if (-not (Test-Path $MainScript)) {
        throw "Main script not found: $MainScript"
    }

    $MainArgs = @($MainScript)
    foreach ($Target in $Targets) {
        $MainArgs += @("--target", $Target)
    }
    $MainArgs += "--no-open"

    Write-Host "Running downloader..."
    & $Runner.Exe @($Runner.PrefixArgs + $MainArgs)
    if ($LASTEXITCODE -ne 0) {
        throw "Downloader failed with exit code $LASTEXITCODE."
    }

    $Credentials = Join-Path $Root "_secrets\google_service_account.json"
    $SyncScript = Join-Path $Root "tools\sync_google_sheet.py"

    if ((Test-Path $Credentials) -and (Test-Path $SyncScript)) {
        Write-Host "Running Google Sheets sync..."
        & $Runner.Exe @($Runner.PrefixArgs + @($SyncScript, "--credentials", $Credentials, "--sheets", "pohang1,gumi1"))
        if ($LASTEXITCODE -ne 0) {
            throw "Google Sheets sync failed with exit code $LASTEXITCODE."
        }
    }
    else {
        Write-Host "Google Sheets sync skipped. Put credentials at _secrets\google_service_account.json to enable it."
    }

    Write-Host "=== Coding classroom update finished: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
}
catch {
    $ExitCode = 1
    Write-Host "ERROR: $($_.Exception.Message)"
}
finally {
    Stop-Transcript | Out-Null
}

exit $ExitCode
