<#
.SYNOPSIS
    Starts the Prefect Server.
.DESCRIPTION
    This script sets up the Prefect logging configuration defined in logging.yml and launches the Prefect Server. Run the script manually for testing if needed, but run as a Windows service for production.
.NOTES
    Expected location: <prefect root>/launch_prefect_server.ps1
#>


# exit on first failure
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = $PSScriptRoot
Write-Output "Script dir: $SCRIPT_DIR"
Set-Location $SCRIPT_DIR

# activate python venv
Invoke-Expression ".\prefect-env\Scripts\Activate.ps1"

# Create logs dir if it doesn't exist
$LOGS_DIR = Join-Path -Path . -ChildPath "logs"
New-Item -ItemType Directory -Force -Path $LOGS_DIR


# test database (default, SQLite)
# Invoke-Expression "prefect config set PREFECT_API_DATABASE_CONNECTION_URL='sqlite+aiosqlite:///file::memory:?cache=shared&uri=true&check_same_thread=false'"

# production database (Postgres, needs to be created first)
# Invoke-Expression "prefect config set PREFECT_API_DATABASE_CONNECTION_URL='postgresql+asyncpg://postgres:admin@localhost:5433/prefect'"

# get path to logging config
$LOGGING_CONFIG_PATH = Join-Path -Path . -ChildPath "logging.yml" -Resolve

# set logging Configuration
Invoke-Expression "prefect config set PREFECT_LOGGING_SETTINGS_PATH=$LOGGING_CONFIG_PATH"

# start Prefect server
Invoke-Expression "prefect server start"