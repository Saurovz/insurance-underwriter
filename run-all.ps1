# run-all.ps1 - Windows PowerShell version

Write-Host "🚀 Starting usecase.ai Platform`n" -ForegroundColor Blue

# Function to check if port is in use
function Test-Port {
    param($Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠️  Port $Port is already in use" -ForegroundColor Yellow
        return $false
    }
    return $true
}

Write-Host "Checking ports..."
if (-not (Test-Port 3000)) { exit 1 }
if (-not (Test-Port 5173)) { exit 1 }
if (-not (Test-Port 3002)) { exit 1 }
if (-not (Test-Port 8000)) { exit 1 }
if (-not (Test-Port 8001)) { exit 1 }

Write-Host "✓ All ports available`n" -ForegroundColor Green

# Store job IDs
$jobs = @()

# Start Landing Page
Write-Host "📱 Starting Landing Page (port 3000)..." -ForegroundColor Blue
$jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\landingzone; npm install 2>`$null; npm run dev" -PassThru

# Start Insurance Backend
Write-Host "🏥 Starting Insurance Backend (port 8000)..." -ForegroundColor Blue
$jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\AI_Insurance_Underwriter\Backend; if (-not (Test-Path .venv)) { uv venv }; .venv\Scripts\Activate.ps1; uv sync; uv run uvicorn api.main:app --host 0.0.0.0 --port 8000" -PassThru

# Start Insurance Frontend
Write-Host "💼 Starting Insurance Frontend (port 5173)..." -ForegroundColor Blue
$jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\AI_Insurance_Underwriter\Frontend; npm install 2>`$null; npm run dev" -PassThru

# Start Video Transcriber Backend
Write-Host "🎬 Starting Video Transcriber Backend (port 8001)..." -ForegroundColor Blue
$jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\videotranscriber\Backend; if (-not (Test-Path .venv)) { uv venv }; .venv\Scripts\Activate.ps1; uv sync; uv run uvicorn api:app --host 0.0.0.0 --port 8001" -PassThru

# Start Video Transcriber Frontend
Write-Host "📹 Starting Video Transcriber Frontend (port 3002)..." -ForegroundColor Blue
$jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\videotranscriber\Frontend; npm install 2>`$null; npm run dev" -PassThru

Start-Sleep -Seconds 5

Write-Host "`n✅ All services started!`n" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "🌐 Landing Page:           http://localhost:3000" -ForegroundColor Green
Write-Host "🏥 Insurance App:          http://localhost:5173" -ForegroundColor Green
Write-Host "📹 Video Transcriber:      http://localhost:3002" -ForegroundColor Green
Write-Host "🔧 Insurance API Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "🔧 Video API:              http://localhost:8001" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "`nPress Ctrl+C in each window to stop services`n" -ForegroundColor Yellow

# Keep script running
Write-Host "Press any key to close this window (services will keep running in other windows)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
