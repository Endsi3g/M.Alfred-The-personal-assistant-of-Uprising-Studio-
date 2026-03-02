# Alfred Master Orchestration Protocol
# Official Uprising Studio Launcher

Write-Host "--- Initializing Alfred Master Orchestration Protocol ---" -ForegroundColor Cyan

$ProjectRoot = Get-Location
$env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"

# Dependency Check
Write-Host "[Alfred] Checking dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

# Launch
Write-Host "[Alfred] Launching Tactical OS..." -ForegroundColor Green
python src/main.py
