# PowerShell script to check if the dashboard service is running and start it if not
$serviceName = "CulturalDashboard8081"
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($null -eq $service) {
    Write-Host "Service '$serviceName' not found."
    exit 1
}
if ($service.Status -ne 'Running') {
    Start-Service -Name $serviceName
    Write-Host "Service '$serviceName' was not running and has been started."
} else {
    Write-Host "Service '$serviceName' is running."
}
