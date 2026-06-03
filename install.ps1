Write-Host "Installing termess..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found, installing..."
    winget install Python.Python.3
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

$venv = "$HOME\.termess-venv"
python -m venv $venv
& "$venv\Scripts\pip" install git+https://github.com/grayshark-same/termess.git

$localBin = "$HOME\.local\bin"
New-Item -ItemType Directory -Force -Path $localBin | Out-Null
Copy-Item "$venv\Scripts\termess.exe" "$localBin\termess.exe" -Force

$userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$localBin*") {
    [System.Environment]::SetEnvironmentVariable("PATH", "$userPath;$localBin", "User")
}

$env:PATH = "$env:PATH;$localBin"

Write-Host "Done! Run: termess init"
