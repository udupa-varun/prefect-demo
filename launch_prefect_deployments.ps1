<#
.SYNOPSIS
    Deploys the configurations defined in serve_deployments.py.
.DESCRIPTION
    This script pushes the deployment definitions contained in serve_deployments.py for any flows that need to be run on Prefect Server. Run the script manually for testing if needed, but run as a Windows service for production.
.NOTES
    Expected location: <prefect root>/launch_prefect_deployments.ps1
#>

# exit on first failure
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = $PSScriptRoot
Write-Output "Script dir: $SCRIPT_DIR"
Set-Location $SCRIPT_DIR

# activate python venv
Invoke-Expression ".\prefect-env\Scripts\Activate.ps1"

# Force-correct API URL
Invoke-Expression "prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api"
# Invoke-Expression "prefect config set PREFECT_API_URL=https://api.prefect.cloud/api/accounts/2a53db77-8a31-48b5-b1fa-015b9c3afc61/workspaces/5f23e60f-8b28-4c97-9718-3fb495e81360"

# Invoke-Expression "prefect config unset PREFECT_LOGGING_SETTINGS_PATH"

# overwrite active deployments
Invoke-Expression "python .\serve_deployments.py"