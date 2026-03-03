# Alfred Master Orchestration Protocol
# Official Uprising Studio Launcher

Write-Host "--- Initializing Alfred Master Orchestration Protocol ---" -ForegroundColor Cyan

$ProjectRoot = Get-Location
$env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"

# Dependency Check
Write-Host "[Alfred] Checking dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

# Ollama Automation Layer
Write-Host "[Alfred] Checking Ollama status..." -ForegroundColor Yellow
$OllamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $OllamaCmd) {
    Write-Host "[Alfred] Ollama not detected. Attempting installation via winget..." -ForegroundColor Cyan
    winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
}

# Start Ollama service if not reachable
$PortCheck = (Test-NetConnection localhost -Port 11434 -InformationLevel Quiet)
if (-not $PortCheck) {
    Write-Host "[Alfred] Starting Ollama Background Service..." -ForegroundColor Green
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# Ensure Local LLM Fallback (llama3)
Write-Host "[Alfred] Syncing Local LLM (llama3)..." -ForegroundColor Yellow
ollama pull llama3

# Launch Alfred HUD & Core
Write-Host "[Alfred] Initializing Alfred Native HUD & Core..." -ForegroundColor Cyan
python src/main.py
