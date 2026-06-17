@echo off

echo ==========================
echo Instalando NORA...
echo ==========================

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python nao encontrado. Instale Python 3.10+
    pause
    exit
)

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Instalacao concluida!
pause
