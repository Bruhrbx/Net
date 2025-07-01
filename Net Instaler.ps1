# installer_chatapp.ps1
# Script ini mengunduh aplikasi Chat App dari GitHub dan menyiapkannya.

# --- KONFIGURASI PENGGUNA ---
# !!! GANTI URL INI DENGAN URL RAW GITHUB ANDA YANG SEBENARNYA !!!
$githubRepoRawUrl = "https://raw.githubusercontent.com/Bruhrbx/Net/main/File/Net.py"
$installDir = "C:\ChatApp" # Direktori tempat aplikasi akan diinstal
$appName = "Chat App"
$pythonExecutable = "python.exe" # Atau "py.exe" jika itu yang Anda gunakan untuk menjalankan Python

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
    Invoke-WebRequest -Uri $githubRepoRawUrl -OutFile (Join-Path $installDir "Uhhhh.py") -UseBasicParsing -ErrorAction Stop
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
    # Menangkap output dan kode keluar untuk debugging
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
"$pythonPath" "$installDir\Uhhhh.py"
pause
"@
Set-Content -Path (Join-Path $installDir "launch.bat") -Value $launcherContent

Write-Host "Skrip peluncur 'launch.bat' berhasil dibuat di $($installDir)." -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "          Instalasi Selesai!          " -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Untuk menjalankan aplikasi, navigasikan ke:" -ForegroundColor White
Write-Host "-> $($installDir)" -ForegroundColor Cyan
Write-Host "Kemudian, klik dua kali 'launch.bat'." -ForegroundColor White
Write-Host ""
Write-Host "Anda juga bisa membuat shortcut desktop untuk 'launch.bat' secara manual." -ForegroundColor DarkGray
Write-Host "Terima kasih telah menggunakan $($appName)!" -ForegroundColor DarkGreen
Read-Host "Tekan Enter untuk keluar..."
