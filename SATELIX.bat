@echo off
title SATELIX AUTOMATION SUITE v2.0 - Interface Moderne
color 0B

echo.
echo +========================================================+
echo ^|                SATELIX AUTOMATION SUITE               ^|
echo ^|                  Interface Moderne                    ^|
echo +========================================================+
echo.

cd /d "%~dp0"

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python non trouve ! Installation requise.
    echo     Telechargez Python depuis https://python.org
    pause
    exit /b 1
)

REM Installer les dependances si necessaire
if not exist "app\.env_deps_installed" (
    echo [*] Installation des dependances modernes...
    pip install -r app\requirements_portable.txt
    if errorlevel 0 (
        echo. > app\.env_deps_installed
        echo [OK] Dependances installees avec succes
    ) else (
        echo [X] Erreur lors de l'installation des dependances
        pause
        exit /b 1
    )
)

REM Lancer l'interface moderne
echo [*] Lancement de l'interface interactive...
python app\cli_interface.py

pause