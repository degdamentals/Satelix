@echo off
cd /d "%~dp0.."

echo Nettoyage des anciens fichiers...
echo.

REM Supprimer les logs de plus de 30 jours
forfiles /p "data\logs" /m "*.log" /d -30 /c "cmd /c del @path" 2>nul

REM Supprimer les captures d'écran de plus de 30 jours
forfiles /p "data\logs" /m "*.png" /d -30 /c "cmd /c del @path" 2>nul

REM Supprimer les fichiers temporaires
del /q data\logs\*.tmp 2>nul

echo ✅ Nettoyage terminé
echo.
echo Les fichiers de plus de 30 jours ont été supprimés.
echo.

exit /b 0