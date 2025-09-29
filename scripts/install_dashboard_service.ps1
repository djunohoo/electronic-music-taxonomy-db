# PowerShell script to create a Windows service for the enhanced dashboard
# This will run the dashboard on startup, even if no user is logged in

$serviceName = "CulturalDashboard8081"
$pythonExe = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
$scriptPath = "E:\\#GITHUB-REPOS\\electronic-music-taxonomy-db\\cultural_dashboard_port8081.py"

# Remove existing service if present
if (Get-Service -Name $serviceName -ErrorAction SilentlyContinue) {
    Stop-Service -Name $serviceName -Force
    sc.exe delete $serviceName | Out-Null
}

# Create the service
sc.exe create $serviceName binPath= '"' + $pythonExe + '" "' + $scriptPath + '"' start= auto

# Set service to run as LocalSystem
sc.exe config $serviceName obj= LocalSystem

# Start the service
Start-Service -Name $serviceName

Write-Host "Service '$serviceName' installed and started. It will run on startup."