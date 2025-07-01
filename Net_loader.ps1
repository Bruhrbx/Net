# 1. Cek Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python tidak ditemukan. Mengarahkan ke situs instalasi..."
    Start-Process "https://www.python.org/downloads/"
    exit
}

# 2. Pastikan pip aktif
Write-Host "🛠 Memastikan pip tersedia..."
python -m ensurepip --default-pip
python -m pip install --upgrade pip

# 3. Instal modul yang diperlukan
$modules = @("tkinter", "psutil", "requests", "pyinstaller")
foreach ($mod in $modules) {
    try {
        Write-Host "📦 Menginstal modul: $mod ..."
        python -m pip install $mod -q
        Write-Host "✅ Modul $mod berhasil diinstal."
    } catch {
        Write-Host "⚠️ Gagal menginstal $mod."
    }
}

# 4. Siapkan folder instalasi
$installPath = "C:\Net"
if (!(Test-Path $installPath)) {
    Write-Host "📁 Membuat folder instalasi di: $installPath"
    New-Item -Path $installPath -ItemType Directory | Out-Null
}

# 5. Unduh file Python ke folder instalasi
$pyUrl = "https://raw.githubusercontent.com/Bruhrbx/Net/main/File/Net's.py"
$appPath = "$installPath\Nets.py"

try {
    Write-Host "🌐 Mengunduh aplikasi..."
    Invoke-WebRequest -Uri $pyUrl -OutFile $appPath
    Write-Host "✅ Aplikasi disimpan di: $appPath"
} catch {
    Write-Host "❌ Gagal mengunduh file Python."
    exit
}

# 6. Jalankan aplikasinya
Write-Host "🚀 Menjalankan aplikasi..."
Start-Process "python" -ArgumentList "`"$appPath`""

# 7. Buat shortcut ke Desktop
$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = $WshShell.CreateShortcut("$desktop\Net App.lnk")
$shortcut.TargetPath = "python"
$shortcut.Arguments = "`"$appPath`""
$shortcut.WorkingDirectory = $installPath
$shortcut.WindowStyle = 1
$shortcut.IconLocation = "python.exe,0"
$shortcut.Save()

Write-Host "📎 Shortcut 'Net App.lnk' telah dibuat di Desktop!"
