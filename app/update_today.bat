@echo off
echo [*] Connexion a Satelix et creation des inventaires...
echo.

cd /d "%~dp0.."

REM Verifier la configuration
if not exist "app\.env" (
    echo [X] Configuration non trouvee. Lancez d'abord la configuration.
    echo     Utilisez l'option [1] du menu principal.
    exit /b 1
)

echo [*] Lancement du processus de creation...
echo +---------------------------------------------+
echo ^| Connexion a Satelix...                     ^|
echo ^| Creation de l'inventaire...                ^|
echo ^| Validation et enregistrement...            ^|
echo +---------------------------------------------+
echo.

REM Lancer la creation
python app\satelix_simple.py --update-today

if errorlevel 2 (
    echo.
    echo [X] ERREUR: Probleme de connexion ou de configuration
    echo [i] Solutions possibles:
    echo     - Verifiez votre connexion au reseau entreprise
    echo     - Lancez le diagnostic [7] depuis le menu
    echo     - Verifiez vos identifiants dans la configuration
) else if errorlevel 1 (
    echo.
    echo [!] ATTENTION: Creation non effectuee
    echo [i] Causes possibles:
    echo     - Inventaire deja existant pour cette date
    echo     - Probleme d'acces a la page inventaires
) else (
    echo.
    echo [OK] SUCCES: Inventaire cree avec succes !
    echo [+] L'inventaire "Inventaire filtres" a ete ajoute
    echo [+] Type: DEPOT / CMUP avec capture des stocks
)

exit /b %errorlevel%