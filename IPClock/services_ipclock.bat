@echo off
REM ========================================
REM   AUTO INSTALL WINDOWS SERVICE (NSSM)
REM   Service Name : IPClockService
REM   Display Name : IPClockService
REM   Description  : Program IP Clock By Puterako
REM ========================================

REM Cek Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Jalankan sebagai Administrator!
    pause
    exit /b 1
)

echo ========================================
echo   INSTALL SERVICE: IPClockService
echo ========================================
echo.

REM Pastikan nssm.exe ada di folder ini
if not exist "%~dp0nssm.exe" (
    echo Error: nssm.exe tidak ditemukan!
    echo.
    echo Download dari: https://nssm.cc/download
    echo Letakkan nssm.exe di folder yang sama.
    pause
    exit /b 1
)

REM Cari file .exe selain nssm.exe
setlocal enabledelayedexpansion
set EXE_FILE=
for %%f in ("%~dp0*.exe") do (
    if /I not "%%~nxf"=="nssm.exe" (
        set EXE_FILE=%%~f
    )
)

if "%EXE_FILE%"=="" (
    echo Tidak ditemukan file .exe selain nssm.exe di folder ini.
    pause
    exit /b 1
)

echo Menginstal service IPClockService...
echo.

REM Install otomatis
"%~dp0nssm.exe" install IPClockService "%EXE_FILE%"
if %errorLevel% neq 0 (
    echo Gagal menginstall service!
    pause
    exit /b 1
)

REM Set informasi service
"%~dp0nssm.exe" set IPClockService DisplayName "IPClockService"
"%~dp0nssm.exe" set IPClockService Description "Program IP Clock By Puterako"
"%~dp0nssm.exe" set IPClockService Start SERVICE_AUTO_START

REM Start service langsung
"%~dp0nssm.exe" start IPClockService

echo.
echo ========================================
echo  Service IPClockService Berhasil Dibuat!
echo ========================================
echo Display Name : IPClockService
echo Deskripsi    : Program IP Clock By Puterako
echo Status       : Running (Auto Start)
echo.
echo Untuk uninstall: nssm remove IPClockService confirm
echo ========================================
pause
