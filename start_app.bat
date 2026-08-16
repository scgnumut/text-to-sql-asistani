@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Text-to-SQL Uygulama Baslatıcı
echo ========================================
echo.

set PROJECT_ROOT=%~dp0
set VENV_DIR=%PROJECT_ROOT%venv
set PYTHON=%VENV_DIR%\Scripts\python.exe

cd /d "%PROJECT_ROOT%"

REM Sanal ortam kontrolu
if not exist "%VENV_DIR%" (
    echo [UYARI] Sanal ortam bulunamadi!
    echo Sanal ortam olusturuluyor...
    
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [HATA] Sanal ortam olusturulamadi.
        pause
        exit /b 1
    )
    
    echo [BASARILI] Sanal ortam olusturuldu.
    echo.
    
    echo [BILGI] Bagimliliklar yukleniyor...
    call "%VENV_DIR%\Scripts\activate.bat"
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [HATA] Bagimliliklar yuklenemedi.
        pause
        exit /b 1
    )
    echo [BASARILI] Bagimliliklar yuklendi.
    echo.
) else (
    echo [BILGI] Sanal ortam bulundu.
)

REM Sanal ortam aktiflestir
echo [BILGI] Sanal ortam aktiflestiriliyor...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [HATA] Sanal ortam aktiflestirilemedi.
    pause
    exit /b 1
)
echo [BASARILI] Sanal ortam aktif.
echo.

REM Python ve bagimlilik kontrol
echo [BILGI] Python ortami kontrol ediliyor...
"%PYTHON%" --version
"%PYTHON%" -c "import streamlit, fastapi, langchain; print('[BASARILI] Tum paketler hazir.')" 2>nul
if errorlevel 1 (
    echo [UYARI] Bazı paketler eksik. Yeniden yukleniyor...
    python -m pip install -r requirements.txt
)
echo.

REM API sunucusunu baslat
echo [1/3] API sunucusu baslatiliyor...
start "Text-to-SQL API" /B python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

echo API hazir olmasi bekleniyor...
:wait_api
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 goto wait_api

echo [BASARILI] API sunucusu http://localhost:8000 adresinde calisiyor
echo.

REM Streamlit uygulamasini baslat
echo [2/3] Streamlit uygulamasi baslatiliyor...
echo.
echo ========================================
echo Uygulama basariyla baslatildi!
echo ========================================
echo API Dokumantasyon: http://localhost:8000/docs
echo API Saglik Kontrolu: http://localhost:8000/health
echo Uygulama:       http://localhost:8501
echo ========================================
echo.

streamlit run src/frontend/app.py

REM Kapatma
echo.
echo [BILGI] Kapatiliyor...
taskkill /FI "WINDOWTITLE eq Text-to-SQL API*" /F >nul 2>&1
echo [BASARILI] Uygulama durduruldu.

endlocal
pause
