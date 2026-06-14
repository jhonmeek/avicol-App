$ErrorActionPreference = "Stop"

$Python = "C:\Users\mouel\AppData\Local\Programs\Python\Python312\python.exe"
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Project

& $Python build_icon.py
& $Python -m PyInstaller --noconfirm --clean AvicolePro.spec

$IsccCandidates = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$Iscc = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($Iscc) {
    & $Iscc installer.iss
    Write-Host "Installateur créé dans $Project\installer"
} else {
    Write-Warning "Inno Setup absent : l'exécutable portable est disponible dans dist\AvicolePro."
}
