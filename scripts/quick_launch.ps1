# Quick launch script for dashboard, API, or scanner
param(
    [string]$Service = "dashboard"
)

switch ($Service) {
    "dashboard" { python cultural_dashboard_port8083.py }
    "api" { python metacrate_api.py }
    "scan" { python cultural_intelligence_system.py --scan "E:\\Music\\Electronic" }
    default { Write-Host "Unknown service: $Service" }
}
