$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$IntervalSeconds = 600
$RunOnceScript = Join-Path $Root "run_update_once.ps1"

if (-not (Test-Path $RunOnceScript)) {
    throw "run_update_once.ps1 not found: $RunOnceScript"
}

Write-Host "Coding classroom auto-update loop started."
Write-Host "Interval: $IntervalSeconds seconds"
Write-Host "Project root: $Root"

while ($true) {
    $StartedAt = Get-Date
    Write-Host ""
    Write-Host "[$($StartedAt.ToString('yyyy-MM-dd HH:mm:ss'))] update cycle started"

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File $RunOnceScript
    $RunExitCode = $LASTEXITCODE

    if ($RunExitCode -ne 0) {
        Write-Host "Update cycle failed with exit code $RunExitCode. The loop will continue."
    }

    $Elapsed = (Get-Date) - $StartedAt
    $SleepSeconds = [Math]::Max(10, $IntervalSeconds - [int]$Elapsed.TotalSeconds)
    Write-Host "Next update in $SleepSeconds seconds."
    Start-Sleep -Seconds $SleepSeconds
}
