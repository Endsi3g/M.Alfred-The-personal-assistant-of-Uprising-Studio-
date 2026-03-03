# Alfred Master Orchestration Protocol
# Official Uprising Studio Launcher

Write-Host "--- Initializing Alfred Master Orchestration Protocol ---" -ForegroundColor Cyan

$ProjectRoot = Get-Location
$env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"


# Ollama Automation Layer
Write-Host "[Alfred] Checking Ollama status..." -ForegroundColor Yellow
$OllamaPath = Get-Command ollama -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if (-not $OllamaPath) {
    # Check common locations
    $PathsToTest = @(
        "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
        "$env:LOCALAPPDATA\Ollama\ollama.exe",
        "C:\Program Files\Ollama\ollama.exe"
    )
    foreach ($p in $PathsToTest) {
        if (Test-Path $p) {
            $OllamaPath = $p
            break
        }
    }
    
    if (-not $OllamaPath) {
        Write-Host "[Alfred] Ollama not detected. Attempting installation via winget..." -ForegroundColor Cyan
        winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
        # Refresh paths after install
        foreach ($p in $PathsToTest) {
            if (Test-Path $p) {
                $OllamaPath = $p
                break
            }
        }
    }
}

# Start Ollama service if not reachable
$PortCheck = (Test-NetConnection localhost -Port 11434 -InformationLevel Quiet)
if (-not $PortCheck) {
    Write-Host "[Alfred] Starting Ollama Background Service..." -ForegroundColor Green
    if ($OllamaPath) {
        Start-Process $OllamaPath -ArgumentList "serve" -WindowStyle Hidden
    } else {
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    }
    Start-Sleep -Seconds 5
}

# Ensure Local LLM Fallback (llama3)
Write-Host "[Alfred] Syncing Local LLM (llama3)..." -ForegroundColor Yellow
if ($OllamaPath) {
    & $OllamaPath pull llama3
} else {
    ollama pull llama3
}

# Launch Alfred HUD & Core
Write-Host "[Alfred] Initializing Alfred Native HUD & Core..." -ForegroundColor Cyan
python src/main.py
