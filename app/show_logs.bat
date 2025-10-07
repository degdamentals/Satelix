@echo off
cd /d "%~dp0.."

echo Affichage des derniers logs...
echo.

REM Afficher le fichier de log principal
if exist "data\logs\satelix_portable.log" (
    echo === DERNIÈRES ACTIVITÉS ===
    echo.

    REM Afficher les 20 dernières lignes
    for /f "skip=1 delims=" %%i in ('more +0 "data\logs\satelix_portable.log"') do (
        echo %%i
    ) | more +0

    echo.
    echo === FIN DES LOGS ===
) else (
    echo ❌ Aucun fichier de log trouvé.
    echo Lancez d'abord une mise à jour pour créer des logs.
)

echo.
echo Fichier complet: data\logs\satelix_portable.log
echo.

exit /b 0