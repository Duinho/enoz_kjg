$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$TaskName = "CodingClassApplicationStatusAutoUpdate"
$StartupFile = Join-Path ([Environment]::GetFolderPath("Startup")) "CodingClassApplicationStatusAutoUpdate.cmd"

$Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $Task) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Startup task removed: $TaskName"
}
else {
    Write-Host "Task not found: $TaskName"
}

if (Test-Path $StartupFile) {
    Remove-Item -LiteralPath $StartupFile -Force
    Write-Host "Startup folder launcher removed: $StartupFile"
}
