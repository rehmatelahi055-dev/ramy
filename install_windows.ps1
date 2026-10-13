#!/usr/bin/env pwsh

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Write-Host "Environment ready. Run: python -m ramy --mode PAPER"
