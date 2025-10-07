@echo off
echo.
echo +========================================================+
echo ^|        PROGRAMMATION AUTOMATISATION QUOTIDIENNE       ^|
echo +========================================================+
echo.

REM Verifier les privileges administrateur
net session >nul 2>&1
if errorlevel 1 (
    echo [X] Ce script doit etre lance en tant qu'administrateur
    echo.
    echo Comment faire:
    echo 1. Fermez cette fenetre
    echo 2. Clic droit sur DEMARRER_SATELIX.bat
    echo 3. "Executer en tant qu'administrateur"
    echo 4. Choisissez l'option [4] a nouveau
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0.."

REM Variables de configuration
set TASK_NAME=Satelix_Portable_Daily
set SCRIPT_PATH=%CD%\app\daily_task.bat
set START_TIME=08:00

echo Configuration de la tâche automatique:
echo - Nom: %TASK_NAME%
echo - Script: %SCRIPT_PATH%
echo - Heure: %START_TIME% (tous les jours ouvrables)
echo.

REM Créer le script de tâche quotidienne
echo @echo off > app\daily_task.bat
echo cd /d "%~dp0.." >> app\daily_task.bat
echo python app\satelix_simple.py --update-today >> app\daily_task.bat

REM Supprimer une tâche existante
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Créer la nouvelle tâche
echo Création de la tâche automatique...
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%SCRIPT_PATH%\"" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st %START_TIME% ^
    /ru "%USERNAME%" ^
    /f

if errorlevel 1 (
    echo ❌ Erreur lors de la création de la tâche
    pause
    exit /b 1
)

echo.
echo [OK] AUTOMATISATION CONFIGUREE !
echo.
echo La creation d'inventaires Satelix se lancera automatiquement:
echo - Tous les jours ouvrables a %START_TIME%
echo - Meme si vous n'etes pas connecte
echo.
echo Pour modifier ou desactiver:
echo 1. Tapez "taskschd.msc" dans le menu Demarrer
echo 2. Cherchez "%TASK_NAME%"
echo 3. Clic droit -^> Proprietes
echo.

REM Test proposé
set /p TEST_NOW="Voulez-vous tester maintenant ? (o/n): "
if /i "%TEST_NOW%"=="o" (
    echo.
    echo Test en cours...
    schtasks /run /tn "%TASK_NAME%"
    echo.
    echo La tâche devrait se lancer dans une nouvelle fenêtre.
)

echo.
echo Configuration terminée !
exit /b 0