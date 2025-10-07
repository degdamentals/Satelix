@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        DIAGNOSTIC SATELIX                                   ║
echo ║                    Résolution des problèmes                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0.."

echo Ce diagnostic va analyser votre configuration et votre connexion.
echo Cela peut prendre quelques minutes...
echo.
pause

REM Lancer le diagnostic Python
python app\diagnostic.py

echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo   Diagnostic terminé
echo ════════════════════════════════════════════════════════════════════════════════
echo.

exit /b 0