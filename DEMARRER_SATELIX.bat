@echo off
title SATELIX AUTOMATION SUITE v2.0
color 0B

:MENU
cls
echo.
echo  +========================================================+
echo  ^|                SATELIX AUTOMATION SUITE               ^|
echo  ^|                     Version 2.0                       ^|
echo  ^|                   Interface Pro                       ^|
echo  +========================================================+
echo.
echo  +-- QUE SOUHAITEZ-VOUS FAIRE ? -------------------------+
echo  ^|                                                       ^|
echo  ^|  [1] Configuration initiale                           ^|
echo  ^|  [2] Creer inventaires (aujourd'hui)                 ^|
echo  ^|  [3] Creer inventaires (date specifique)             ^|
echo  ^|  [4] Automatisation quotidienne                      ^|
echo  ^|  [5] Consulter les logs                              ^|
echo  ^|  [6] Nettoyage des fichiers                          ^|
echo  ^|  [7] Diagnostic systeme                              ^|
echo  ^|  [8] Reparation automatique                          ^|
echo  ^|  [9] Mode debug (Chrome visible)                     ^|
echo  ^|  [0] Quitter                                          ^|
echo  ^|                                                       ^|
echo  +-------------------------------------------------------+
echo.
set /p choice=" Votre choix (0-9): "

if "%choice%"=="1" goto SETUP
if "%choice%"=="2" goto UPDATE_TODAY
if "%choice%"=="3" goto UPDATE_DATE
if "%choice%"=="4" goto SCHEDULE
if "%choice%"=="5" goto LOGS
if "%choice%"=="6" goto CLEANUP
if "%choice%"=="7" goto DIAGNOSTIC
if "%choice%"=="8" goto FIX_CONNECTION
if "%choice%"=="9" goto DEBUG_MODE
if "%choice%"=="0" goto EXIT

echo.
echo  [X] Choix invalide ! Veuillez selectionner un numero entre 0 et 9.
echo.
timeout /t 2 >nul
goto MENU

:SETUP
cls
echo.
echo  +========================================================+
echo  ^|                CONFIGURATION INITIALE                 ^|
echo  +========================================================+
echo.
echo  +-- ETAPES DE CONFIGURATION ----------------------------+
echo  ^|                                                       ^|
echo  ^|  1. Verification de l'environnement Python           ^|
echo  ^|  2. Installation des dependances                     ^|
echo  ^|  3. Configuration des identifiants Satelix           ^|
echo  ^|  4. Test de connexion                                ^|
echo  ^|                                                       ^|
echo  +-------------------------------------------------------+
echo.
echo  [!] Assurez-vous d'avoir vos identifiants Satelix !
echo.
pause
call app\setup_portable.bat
pause
goto MENU

:UPDATE_TODAY
cls
echo.
echo  +========================================================+
echo  ^|              CREATION D'INVENTAIRES                   ^|
echo  ^|                 (Date du jour)                        ^|
echo  +========================================================+
echo.
echo  +-- TRAITEMENT EN COURS --------------------------------+
echo  ^|                                                       ^|
echo  ^|  Date: %date%                                        ^|
echo  ^|  Action: Creation automatique d'inventaires          ^|
echo  ^|  Type: Inventaire filtres / DEPOT / CMUP             ^|
echo  ^|                                                       ^|
echo  +-------------------------------------------------------+
echo.
call app\update_today.bat
echo.
echo  [OK] Termine ! Appuyez sur une touche pour continuer...
pause >nul
goto MENU

:UPDATE_DATE
cls
echo.
echo  ╔════════════════════════════════════════════════════════╗
echo  ║            📅 CRÉATION DATE SPÉCIFIQUE 📅              ║
echo  ╚════════════════════════════════════════════════════════╝
echo.
echo  ┌─ 📋 SAISIE DE LA DATE ──────────────────────────────────┐
echo  │                                                         │
echo  │  Format requis: JJ/MM/AAAA                             │
echo  │  Exemple: 25/12/2025                                   │
echo  │                                                         │
echo  └─────────────────────────────────────────────────────────┘
echo.
set /p target_date=" 📅 Entrez la date cible: "
echo.
echo  ┌─ 🚀 TRAITEMENT EN COURS ────────────────────────────────┐
echo  │  📅 Date cible: %target_date%                          │
echo  │  🎯 Création d'inventaires en cours...                 │
echo  └─────────────────────────────────────────────────────────┘
call app\update_date.bat "%target_date%"
echo.
echo  ✅ Terminé ! Appuyez sur une touche pour continuer...
pause >nul
goto MENU

:SCHEDULE
cls
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║           AUTOMATISATION QUOTIDIENNE         ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Configuration de l'automatisation quotidienne...
echo  (Nécessite les droits administrateur)
echo.
pause
call app\setup_schedule.bat
pause
goto MENU

:LOGS
cls
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║              DERNIERS LOGS                   ║
echo  ╚══════════════════════════════════════════════╝
echo.
call app\show_logs.bat
echo.
echo  Appuyez sur une touche pour continuer...
pause >nul
goto MENU

:CLEANUP
cls
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║             NETTOYAGE FICHIERS               ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Suppression des fichiers de plus de 30 jours...
call app\cleanup.bat
echo.
echo  Nettoyage terminé ! Appuyez sur une touche pour continuer...
pause >nul
goto MENU

:DIAGNOSTIC
cls
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║            DIAGNOSTIC DE CONNEXION           ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Analyse de votre configuration et connexion...
echo  (Utile en cas de problème de connexion)
echo.
pause
call app\diagnostic.bat
pause
goto MENU

:FIX_CONNECTION
cls
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║         CORRECTIFS AUTOMATIQUES              ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Application automatique de correctifs...
echo  (Résolution d'URL, ports, DNS, etc.)
echo.
pause
python app\fix_connection.py
echo.
echo  Correctifs terminés ! Appuyez sur une touche pour continuer...
pause >nul
goto MENU

:DEBUG_MODE
cls
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║              MODE DEBUG CHROME               ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Lancement avec fenêtre Chrome visible...
echo  (Pour voir exactement ce qui se passe)
echo.
call app\debug_mode.bat
echo.
echo  Debug terminé ! Appuyez sur une touche pour continuer...
pause >nul
goto MENU

:EXIT
cls
echo.
echo  +========================================================+
echo  ^|                   AU REVOIR !                         ^|
echo  +========================================================+
echo.
echo  +-- MERCI ! --------------------------------------------+
echo  ^|                                                       ^|
echo  ^|  Merci d'avoir utilise Satelix Automation Suite      ^|
echo  ^|  Votre productivite vient d'augmenter !              ^|
echo  ^|                                                       ^|
echo  ^|  Support: Consultez les guides dans le dossier       ^|
echo  ^|                                                       ^|
echo  +-------------------------------------------------------+
echo.
echo  Fermeture dans 3 secondes...
timeout /t 3 >nul
exit

:ERROR
echo.
echo  ❌ Une erreur s'est produite.
echo  Consultez le fichier data\logs\error.log pour plus d'informations.
echo.
pause
goto MENU