# Cultural Intelligence System - Auto Restart Script
# Checks every hour and restarts if needed

$apiUrl = "http://172.22.17.37:5000/health"
$scriptDir = "E:\#GITHUB-REPOS\electronic-music-taxonomy-db"
$logFile = "$scriptDir\cultural_intelligence_monitor.log"

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Add-Content -Path $logFile
}

function Test-APIHealth {
    try {
        $response = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            $content = $response.Content | ConvertFrom-Json
            Write-Log "✅ API healthy - Uptime: $($content.uptime_seconds) seconds"
            return $true
        } else {
            Write-Log "⚠️  API responding but status: $($response.StatusCode)"
            return $false
        }
    }
    catch {
        Write-Log "❌ API health check failed: $($_.Exception.Message)"
        return $false
    }
}

function Start-CulturalAPI {
    try {
        # Kill any existing python processes running the API
        Get-Process -Name "python" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*simple_rest_api.py*" } | 
        Stop-Process -Force
        
        Start-Sleep -Seconds 2
        
        # Start new instance
        Set-Location $scriptDir
        Start-Process python -ArgumentList "simple_rest_api.py" -WindowStyle Hidden
        
        Start-Sleep -Seconds 5
        
        Write-Log "🚀 Started Cultural Intelligence API"
        return $true
    }
    catch {
        Write-Log "❌ Failed to start API: $($_.Exception.Message)"
        return $false
    }
}

# Main monitoring logic
Write-Log "🔍 Cultural Intelligence Monitor - Starting health check"

if (-not (Test-APIHealth)) {
    Write-Log "⚠️  API not healthy, attempting restart..."
    
    if (Start-CulturalAPI) {
        Start-Sleep -Seconds 10
        if (Test-APIHealth) {
            Write-Log "✅ API successfully restarted and healthy"
        } else {
            Write-Log "❌ API restart failed - still not responding"
        }
    }
} else {
    Write-Log "✅ API is healthy, no action needed"
}

Write-Log "Monitor check completed"