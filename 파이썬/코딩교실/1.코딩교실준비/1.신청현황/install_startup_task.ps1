$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskName = "CodingClassApplicationStatusAutoUpdate"
$StartScript = Join-Path $Root "start_auto_update.ps1"
$StartupFileName = "CodingClassApplicationStatusAutoUpdate.cmd"

if (-not (Test-Path $StartScript)) {
    throw "start_auto_update.ps1 not found: $StartScript"
}

function Start-AutoUpdateLoop {
    $existing = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*start_auto_update.ps1*" -and $_.CommandLine -like "*$Root*" } |
        Select-Object -First 1

    if ($existing) {
        Write-Host "Auto-update loop is already running. PID: $($existing.ProcessId)"
        return
    }

    Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Minimized", "-File", $StartScript `
        -WindowStyle Minimized

    Write-Host "Auto-update loop started."
}

function Install-StartupFolderFallback {
    $startupDir = [Environment]::GetFolderPath("Startup")
    $startupFile = Join-Path $startupDir $StartupFileName
    $command = "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File `"$StartScript`"`r`n"

    Set-Content -Path $startupFile -Value $command -Encoding Default
    Write-Host "Startup folder launcher installed."
    Write-Host "Startup file: $startupFile"
    Start-AutoUpdateLoop
}

try {
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
}
catch {
    Write-Host "Scheduled task install failed: $($_.Exception.Message)"
    Write-Host "Falling back to the user's Startup folder."
    Install-StartupFolderFallback
}
