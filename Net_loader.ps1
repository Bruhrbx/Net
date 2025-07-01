# installer_chatapp.ps1
# Script ini mengunduh aplikasi Chat App dari GitHub dan menyiapkannya.

# --- KONFIGURASI PENGGUNA ---
$githubRepoRawUrl = "https://raw.githubusercontent.com/Bruhrbx/Net/main/File/Net.py"
$installDir = "C:\ChatApp\"                    # Direktori tempat aplikasi akan diinstal
$appName = "Net's"
$pythonExecutable = "python.exe"              # Ganti ke "py.exe" jika kamu pakai itu
$pythonAppFileName = "Net's.py"               # Nama file Python yang akan diunduh dan dijalankan

# --- PROSES INSTALASI ---
Write-Host "Memulai instalasi $appName..." -ForegroundColor Green

# 1. Buat direktori instalasi
Write-Host "Membuat direktori instalasi: $installDir..."
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "Direktori berhasil dibuat." -ForegroundColor Green
} else {
    Write-Host "Direktori sudah ada. Menggunakan direktori yang sudah ada." -ForegroundColor Yellow
}

# 2. Unduh skrip Python
Write-Host "Mengunduh skrip $appName dari GitHub..."
try {
    Invoke-WebRequest -Uri $githubRepoRawUrl -OutFile (Join-Path $installDir $pythonAppFileName) -UseBasicParsing -ErrorAction Stop
    Write-Host "Skrip berhasil diunduh ke $installDir." -ForegroundColor Green
} catch {
    Write-Error "Gagal mengunduh skrip. Periksa URL GitHub dan koneksi internet Anda."
    Write-Error "Error: $($_.Exception.Message)"
    exit 1
}

# 3. Periksa Python dan instal dependensi
Write-Host "Memeriksa Python dan menginstal dependensi (psutil)..."
try {
    $pythonPath = Get-Command $pythonExecutable -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path
    if (-not $pythonPath) {
        Write-Error "Eksekusi Python '$pythonExecutable' tidak ditemukan. Mohon instal Python dan pastikan itu ada di PATH."
        Write-Host "Unduh Python dari: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }

    # Instal dependensi
    Write-Host "Menginstal psutil..."
    $pipInstallResult = & "$pythonPath" -m pip install psutil 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Gagal menginstal psutil. Output: $pipInstallResult"
    } else {
        Write-Host "psutil berhasil diinstal." -ForegroundColor Green
    }

} catch {
    Write-Error "Kesalahan saat instalasi dependensi: $($_.Exception.Message)"
    exit 1
}

# 4. Buat skrip peluncur (.bat)
Write-Host "Membuat skrip peluncur 'launch.bat'..."
$launcherContent = @"
@echo off
"$pythonPath" "$installDir\$pythonAppFileName"
pause
"@
Set-Content -Path (Join-Path $installDir "launch.bat") -Value $launcherContent
Write-Host "Peluncur 'launch.bat' berhasil dibuat di $installDir." -ForegroundColor Green

# 5. Tampilkan status instalasi
Write-Host "`n=========================================" -ForegroundColor Yellow
Write-Host "         Instalasi $appName Selesai!        " -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow

# 6. Shortcut desktop & peluncuran aplikasi
$choice = Read-Host "Ingin meluncurkan aplikasi sekarang dan membuat shortcut desktop? (y/n)"

Write-Host "Membuat shortcut desktop..."
try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcutPath = (Join-Path $shell.SpecialFolders.Desktop "$appName.lnk")
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = (Join-Path $installDir "launch.bat")
    $shortcut.WorkingDirectory = $installDir
    $shortcut.Save()
    Write-Host "Shortcut berhasil dibuat: $shortcutPath" -ForegroundColor Green
} catch {
    Write-Warning "Gagal membuat shortcut desktop. Error: $($_.Exception.Message)"
}

# Jalankan jika pengguna setuju
if ($choice -eq 'y') {
    Write-Host "Meluncurkan $appName..."
    try {
        Start-Process (Join-Path $installDir "launch.bat")
    } catch {
        Write-Warning "Gagal meluncurkan aplikasi. Jalankan 'launch.bat' secara manual. Error: $($_.Exception.Message)"
    }
} else {
    Write-Host "Aplikasi tidak diluncurkan sekarang." -ForegroundColor Yellow
    Write-Host "Gunakan shortcut desktop atau file 'launch.bat' untuk membuka aplikasi." -ForegroundColor White
}

# 7. Akhiri
Write-Host "`nTerima kasih telah menggunakan $appName!" -ForegroundColor DarkGreen
Read-Host "Tekan Enter untuk keluar..."
