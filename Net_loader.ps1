# installer_chatapp.ps1
# Script ini mengunduh aplikasi Chat App dari GitHub dan menyiapkannya.

# --- KONFIGURASI PENGGUNA ---
# !!! GANTI URL INI DENGAN URL RAW GITHUB ANDA YANG SEBENARNYA !!!
$githubRepoRawUrl = "https://raw.githubusercontent.com/Bruhrbx/Net/main/File/Net.py"
$installDir = "C:\ChatApp\" # Direktori tempat aplikasi akan diinstal
$appName = "Net's"
$pythonExecutable = "python.exe" # Atau "py.exe" jika itu yang Anda gunakan untuk menjalankan Python
$pythonAppFileName = "Net's.py" # Nama file Python yang akan diunduh dan dijalankan

# --- JANGAN UBAH KODE DI BAWAH INI KECUALI ANDA TAHU APA YANG ANDA LAKUKAN ---

Write-Host "Memulai instalasi $($appName)..." -ForegroundColor Green

# 1. Buat direktori instalasi
Write-Host "Membuat direktori instalasi: $($installDir)..."
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "Direktori berhasil dibuat." -ForegroundColor Green
} else {
    Write-Host "Direktori sudah ada. Menggunakan direktori yang sudah ada." -ForegroundColor Yellow
}

# 2. Unduh skrip Python
Write-Host "Mengunduh skrip $($appName) dari GitHub..."
try {
    Invoke-WebRequest -Uri $githubRepoRawUrl -OutFile (Join-Path $installDir $pythonAppFileName) -UseBasicParsing -ErrorAction Stop
    Write-Host "Skrip berhasil diunduh ke $($installDir)." -ForegroundColor Green
} catch {
    Write-Error "Gagal mengunduh skrip. Mohon periksa URL GitHub dan koneksi internet Anda."
    Write-Error "Error: $($_.Exception.Message)"
    exit 1
}

# 3. Periksa Python dan instal dependensi
Write-Host "Memeriksa Python dan menginstal dependensi (psutil)..."
try {
    # Coba temukan eksekusi Python
    $pythonPath = Get-Command $pythonExecutable -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path
    if (-not $pythonPath) {
        Write-Error "Eksekusi Python '$($pythonExecutable)' tidak ditemukan. Mohon instal Python dan pastikan itu ada di PATH Anda."
        Write-Host "Anda dapat mengunduh Python dari https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }

    # Instal psutil
    Write-Host "Menginstal psutil..."
    $pipInstallResult = & "$pythonPath" -m pip install psutil 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Gagal menginstal psutil. Ini mungkin menyebabkan masalah. Output: $($pipInstallResult)"
    } else {
        Write-Host "psutil berhasil diinstal." -ForegroundColor Green
    }

} catch {
    Write-Error "Terjadi kesalahan selama instalasi dependensi Python: $($_.Exception.Message)"
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

Write-Host "Skrip peluncur 'launch.bat' berhasil dibuat di $($installDir)." -ForegroundColor Green

Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "          Instalasi Selesai! :D          " -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow

# --- PROMPT BARU DAN PEMBUATAN SHORTCUT ---
Write-Host ""
$choice = Read-Host "Apakah Anda ingin meluncurkan aplikasi sekarang dan membuat shortcut di desktop? (y/n)"

# Selalu buat shortcut desktop (sesuai permintaan "kalau n nanti membuat shortcut di desktop")
Write-Host "Membuat shortcut desktop..."
try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcutPath = (Join-Path $shell.SpecialFolders.Desktop "$($appName).lnk")
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = (Join-Path $installDir "launch.bat")
    $shortcut.WorkingDirectory = $installDir
    # Opsional: Atur ikon jika Anda punya file ikon (.ico) di direktori instalasi
    # $shortcut.IconLocation = (Join-Path $installDir "nama_icon_anda.ico")
    $shortcut.Save()
    Write-Host "Shortcut desktop berhasil dibuat: $($shortcutPath)" -ForegroundColor Green
} catch {
    Write-Warning "Gagal membuat shortcut desktop. Error: $($_.Exception.Message)"
}

# Logika untuk meluncurkan aplikasi berdasarkan pilihan pengguna
if ($choice -eq 'y') {
    Write-Host "Meluncurkan $($appName)..."
    try {
        Start-Process (Join-Path $installDir "launch.bat")
    } catch {
        Write-Warning "Gagal meluncurkan aplikasi. Mohon jalankan 'launch.bat' dari $($installDir) secara manual. Error: $($_.Exception.Message)"
    }
} else {
    Write-Host "Aplikasi tidak akan diluncurkan sekarang." -ForegroundColor Yellow
    Write-Host "Anda dapat menjalankan aplikasi dari shortcut desktop atau dengan menjalankan 'launch.bat' di $($installDir)." -ForegroundColor White
}

Write-Host ""
Write-Host "Terima kasih telah menggunakan $($appName)!" -ForegroundColor DarkGreen
Read-Host "Tekan Enter untuk keluar..."
}

Write-Host ""
Write-Host "Terima kasih telah menggunakan $($appName)!" -ForegroundColor DarkGreen
Read-Host "Tekan Enter untuk keluar..."
}
