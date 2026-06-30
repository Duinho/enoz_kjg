$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$RunOnceScript = Join-Path $Root "run_update_once.ps1"

if (-not (Test-Path $RunOnceScript)) {
    throw "run_update_once.ps1 not found: $RunOnceScript"
}

function Get-NextTenMinuteSlot {
    param([datetime]$After)

    $ThisHour = $After.Date.AddHours($After.Hour)
    for ($Minute = 0; $Minute -lt 60; $Minute += 10) {
        $Slot = $ThisHour.AddMinutes($Minute)
        if ($After -le $Slot.AddSeconds(30)) {
            return $Slot
        }
    }

    return $ThisHour.AddHours(1)
}

function Wait-Until {
    param([datetime]$Target)

    while ($true) {
        $SleepSeconds = [int][Math]::Ceiling(($Target - (Get-Date)).TotalSeconds)
        if ($SleepSeconds -le 0) {
            return
        }

        Start-Sleep -Seconds ([Math]::Min($SleepSeconds, 300))
    }
}

Write-Host "Coding classroom auto-update loop started."
Write-Host "Schedule: every 10 minutes"
Write-Host "Project root: $Root"

$NextRun = Get-NextTenMinuteSlot -After (Get-Date)

while ($true) {
    Write-Host ""
    Write-Host "Next update scheduled for $($NextRun.ToString('yyyy-MM-dd HH:mm:ss'))"
    Wait-Until -Target $NextRun

    $StartedAt = Get-Date
    Write-Host ""
    Write-Host "[$($StartedAt.ToString('yyyy-MM-dd HH:mm:ss'))] update cycle started"

    powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $RunOnceScript
    $RunExitCode = $LASTEXITCODE

    if ($RunExitCode -ne 0) {
        Write-Host "Update cycle failed with exit code $RunExitCode. The loop will continue."
    }

    $NextRun = $NextRun.AddMinutes(10)
    while ($NextRun -le (Get-Date)) {
        $NextRun = $NextRun.AddMinutes(10)
    }
}
