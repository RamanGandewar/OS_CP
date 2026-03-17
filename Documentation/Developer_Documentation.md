# Developer Documentation

## Code Structure

- `Backend/` contains Flask routes, models, and database scripts
- `Frontend/` contains the React UI
- `Phase_*` folders contain phase-specific logic, outputs, and analytics

## Unified Dashboard API

- `GET /api/dashboard/snapshot`
- `POST /api/dashboard/analytics/generate`
- `GET /api/dashboard/export/csv`
- `GET /api/dashboard/report`
- `GET /api/dashboard/stream`

## Deployment Guide

- Local launcher: `python CRM.py`
- PowerShell helper: `scripts/run_final_dashboard.ps1`
