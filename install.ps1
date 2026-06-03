Write-Host "Installing termess..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found, installing..."
    winget install Python.Python.3
}

if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "pip not found, installing..."
    python -m ensurepip
}

pip install git+https://github.com/grayshark-same/termess.git

Write-Host "Done! Run: termess init"
