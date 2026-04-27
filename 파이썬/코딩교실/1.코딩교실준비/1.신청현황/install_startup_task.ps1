$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskName = "CodingClassApplicationStatusAutoUpdate"
$StartScript = Join-Path $Root "start_auto_update.ps1"

if (-not (Test-Path $StartScript)) {
    throw "start_auto_update.ps1 not found: $StartScript"
}

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File `"$StartScript`""

$Trigger = New-ScheduledTaskTrigger -AtLogOn

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Update coding classroom application status every 10 minutes after Windows logon." `
    -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName

Write-Host "Startup task installed and started."
Write-Host "Task name: $TaskName"
Write-Host "Script: $StartScript"
