# Script PowerShell untuk menginstal Python, tkinter, psutil, dan setup Net's
Write-Host "================================="
Write-Host "=  Welcome to loader Net's 📦!  ="
Write-Host "= https://discord.gg/f9HGQkDGgb ="
Write-Host "================================="
Write-Host ""

# 1. Menginstal Python (dengan pip) jika belum terinstal
if (-not (Test-Path -Path "C:\Python*")) {
    Write-Host "🐍 Menginstal Python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
    Start-Process -Wait -FilePath "$env:TEMP\python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"
    Remove-Item -Path "$env:TEMP\python-installer.exe"
}

# 2. Memastikan pip dan modul yang diperlukan terinstal
Write-Host "🔍️ Memastikan pip dan modul yang diperlukan terinstal..."
python -m pip install --upgrade pip
pip install psutil

# tkinter biasanya sudah termasuk dalam instalasi Python standar
# Jika ada error, kita bisa menginstalnya dengan:
# pip install tk

# 3. Membuat folder C:/Net's/ jika belum ada
$netsFolder = "C:\Net's"
if (-not (Test-Path -Path $netsFolder)) {
    New-Item -ItemType Directory -Path $netsFolder -Force
}

# 4. Mengunduh Net.py dari GitHub
$netUrl = "https://github.com/Bruhrbx/Net/raw/main/File/Net.py"
$netPath = "$netsFolder\Net.py"
Write-Host "🔍️ Memastikan Dan Mengunduh Net.py dari GitHub..."
Invoke-WebRequest -Uri $netUrl -OutFile $netPath

# 5. Membuat shortcut di desktop
$shortcutPath = "$env:USERPROFILE\Desktop\Net's.lnk"
$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "python"
$shortcut.Arguments = "`"$netPath`""
$shortcut.WorkingDirectory = $netsFolder
$shortcut.IconLocation = "$netPath,0"
$shortcut.Save()

Write-Host "============================================================"
Write-Host "Instalasi selesai. Shortcut Net's telah dibuat di desktop. :D"
Write-Host "============================================================"
