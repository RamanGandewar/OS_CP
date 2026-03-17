$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
& ".\Backend\venv\Scripts\python.exe" "Phase_9_Integration_Dashboard\code\final_validation_test.py"
