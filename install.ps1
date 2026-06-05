Write-Host "Installing termess..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found, installing..."
    winget install Python.Python.3 --silent
    # обновить PATH после установки
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python still not found. Install manually: https://python.org"
    exit 1
}

$venv = "$HOME\.termess-venv"
python -m venv $venv

if (-not (Test-Path "$venv\Scripts\pip.exe")) {
    Write-Host "Failed to create venv"
    exit 1
}

& "$venv\Scripts\pip" install git+https://github.com/grayshark-same/termess.git

$localBin = "$HOME\.local\bin"
New-Item -ItemType Directory -Force -Path $localBin | Out-Null
Copy-Item "$venv\Scripts\termess.exe" "$localBin\termess.exe" -Force

$userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$localBin*") {
    [System.Environment]::SetEnvironmentVariable("PATH", "$userPath;$localBin", "User")
}

$env:PATH = "$env:PATH;$localBin"

Write-Host "Done! Restart terminal and run: termess init"
