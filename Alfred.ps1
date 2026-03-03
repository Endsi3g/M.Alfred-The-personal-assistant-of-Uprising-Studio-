# Alfred Master Orchestration Protocol
# Official Uprising Studio Launcher

Write-Host "--- Initializing Alfred Master Orchestration Protocol ---" -ForegroundColor Cyan

$ProjectRoot = Get-Location
$env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"

# Dependency Check
Write-Host "[Alfred] Checking dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

# Launch Python Core API/Backend (in background)
Write-Host "[Alfred] Launching Tactical OS Core..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "src/main.py"

# Wait a moment for FastAPI/Websockets to be ready
Start-Sleep -Seconds 3

# Launch Cluely Overlay Frontend
Write-Host "[Alfred] Launching Cluely Overlay Engine..." -ForegroundColor Cyan
Set-Location "$ProjectRoot\cluely-overlay"
npm start
