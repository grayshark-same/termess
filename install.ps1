Write-Host "Installing termess..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found, installing..."
    $installer = "$env:TEMP\python_installer.exe"
    Invoke-WebRequest "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" -OutFile $installer
    Start-Process $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1" -Wait
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Failed to install Python. Install manually: https://python.org"
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
