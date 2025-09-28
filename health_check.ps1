# Simple Cultural Intelligence Health Check
# Run this hourly to ensure API stays running

$apiUrl = "http://172.22.17.37:5000/health"
$scriptDir = "E:\#GITHUB-REPOS\electronic-music-taxonomy-db"

Write-Host "Checking Cultural Intelligence API..."

try {
    $response = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is healthy"
        exit 0
    } else {
        Write-Host "⚠️  API not responding properly"
        throw "Bad status code"
    }
}
catch {
    Write-Host "❌ API failed, restarting..."
    
    # Kill existing processes
    Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Wait and restart
    Start-Sleep -Seconds 3
    Set-Location $scriptDir
    Start-Process python -ArgumentList "simple_rest_api.py" -WindowStyle Hidden
    
    Write-Host "🚀 Restarted Cultural Intelligence API"
}