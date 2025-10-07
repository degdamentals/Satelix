@echo off
set target_date=%~1

if "%target_date%"=="" (
    echo ❌ Aucune date spécifiée
    exit /b 1
)

echo Mise à jour des inventaires vers %target_date%...

cd /d "%~dp0.."

REM Vérifier la configuration
if not exist "app\.env" (
    echo ❌ Configuration non trouvée. Lancez d'abord la configuration.
    exit /b 1
)

REM Lancer la mise à jour avec date spécifique
python app\satelix_simple.py --update-date "%target_date%"

if errorlevel 2 (
    echo ❌ Erreur de connexion ou date invalide
    echo Vérifiez le format de date (DD/MM/YYYY) et votre connexion
) else if errorlevel 1 (
    echo ⚠️  Aucune mise à jour nécessaire ou inventaires introuvables
) else (
    echo ✅ Mise à jour vers %target_date% terminée avec succès
)

exit /b %errorlevel%