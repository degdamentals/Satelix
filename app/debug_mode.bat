@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            MODE DEBUG                                       ║
echo ║                   (Fenêtre Chrome visible)                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0.."

echo Ce mode va lancer Satelix avec la fenêtre Chrome VISIBLE
echo pour que vous puissiez voir exactement ce qui se passe.
echo.
echo Utile pour diagnostiquer les problèmes de connexion.
echo.
pause

REM Modifier temporairement le fichier .env pour désactiver headless
if exist "app\.env" (
    echo HEADLESS=false > app\.env.tmp
    type app\.env | findstr /v "HEADLESS=" >> app\.env.tmp
    move app\.env.tmp app\.env.debug
    move app\.env app\.env.backup
    move app\.env.debug app\.env
)

echo Mode debug activé (Chrome visible)
echo.

REM Lancer la mise à jour en mode debug
python app\satelix_simple.py --update-today

echo.
echo Debug terminé. Restoration du mode normal...

REM Restaurer le fichier .env original
if exist "app\.env.backup" (
    move app\.env app\.env.debug
    move app\.env.backup app\.env
    echo Mode normal restauré
)

echo.
echo Les captures d'écran de debug sont dans: data\logs\
echo.
pause