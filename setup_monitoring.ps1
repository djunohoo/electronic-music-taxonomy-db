# Setup Scheduled Task for Cultural Intelligence Monitoring
# Run this script as Administrator

$taskName = "CulturalIntelligenceMonitor"
$scriptPath = "E:\#GITHUB-REPOS\electronic-music-taxonomy-db\monitor_cultural_intelligence.ps1"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "⚠️  Task '$taskName' already exists. Removing it first..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create new scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Cultural Intelligence System health monitoring and auto-restart"

Write-Host "✅ Scheduled task '$taskName' created successfully!"
Write-Host "   - Runs every hour"
Write-Host "   - Checks API health at http://172.22.17.37:5000/health"  
Write-Host "   - Restarts API if not responding"
Write-Host "   - Logs to cultural_intelligence_monitor.log"

# Start the task immediately for testing
Start-ScheduledTask -TaskName $taskName

Write-Host "🧪 Started task immediately for testing..."
Start-Sleep -Seconds 10

# Check log file
$logFile = "E:\#GITHUB-REPOS\electronic-music-taxonomy-db\cultural_intelligence_monitor.log"
if (Test-Path $logFile) {
    Write-Host "📄 Recent log entries:"
    Get-Content $logFile | Select-Object -Last 5
}

Write-Host "✅ Cultural Intelligence System monitoring is now active!"