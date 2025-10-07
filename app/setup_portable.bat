@echo off
echo.
echo ================================================
echo     CONFIGURATION INITIALE SATELIX PORTABLE
echo ================================================
echo.

REM Aller dans le dossier de l'application
cd /d "%~dp0.."

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé sur cette machine.
    echo.
    echo SOLUTION AUTOMATIQUE:
    echo 1. Téléchargement de Python portable en cours...
    echo.

    REM Télécharger Python portable (version embeddable)
    if not exist "python\python.exe" (
        echo Téléchargement de Python portable...
        mkdir python 2>nul

        REM Note: En production, on peut inclure Python portable directement
        echo Pour l'instant, veuillez installer Python depuis python.org
        echo Puis relancez cette configuration.
        pause
        exit /b 1
    )
) else (
    echo ✅ Python trouvé
)

REM Installer les dépendances
echo.
echo Installation des dépendances...
pip install -r app\requirements_portable.txt
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo ✅ Dépendances installées

REM Configuration des identifiants
echo.
echo ================================================
echo          CONFIGURATION DES IDENTIFIANTS
echo ================================================
echo.
echo Veuillez entrer vos informations Satelix:
echo.

if not exist "app\.env" (
    REM Créer le fichier .env depuis les entrées utilisateur
    set /p url_login="URL de connexion Satelix (ex: http://sql-industrie:7980/): "
    set /p username="Nom d'utilisateur: "
    set /p password="Mot de passe: "

    echo # Configuration Satelix Portable > app\.env
    echo SATELIX_URL_LOGIN=!url_login! >> app\.env
    echo SATELIX_URL_INVENTAIRES=!url_login!inventaire >> app\.env
    echo SATELIX_USER=!username! >> app\.env
    echo SATELIX_PASSWORD=!password! >> app\.env
    echo. >> app\.env
    echo # Configuration >> app\.env
    echo HEADLESS=true >> app\.env
    echo TIMEOUT=30 >> app\.env

    echo ✅ Configuration sauvegardée
) else (
    echo ✅ Configuration existante trouvée
    set /p reconfigure="Reconfigurer les identifiants ? (o/n): "
    if /i "!reconfigure!"=="o" (
        del app\.env
        goto RECONFIG
    )
)

REM Test de la configuration
echo.
echo Test de la configuration...
python app\test_config.py
if errorlevel 1 (
    echo ❌ Erreur dans la configuration
    echo Vérifiez vos identifiants et l'URL
    pause
    exit /b 1
)

echo ✅ Configuration OK

REM Créer les dossiers nécessaires
mkdir data\logs 2>nul
mkdir data\logs\daily 2>nul
mkdir data\logs\screenshots 2>nul

echo.
echo ================================================
echo         CONFIGURATION TERMINÉE !
echo ================================================
echo.
echo Votre application Satelix portable est prête.
echo Vous pouvez maintenant:
echo.
echo 1. Mettre à jour les inventaires
echo 2. Programmer l'automatisation
echo 3. Copier ce dossier sur une clé USB
echo.
echo Cette configuration fonctionne sur n'importe quel PC
echo avec les mêmes identifiants Satelix.
echo.

exit /b 0

:RECONFIG
REM Jump point for reconfiguration
goto :eof