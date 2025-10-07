#!/usr/bin/env python3
"""
Interface CLI moderne pour Satelix Automation Suite
Utilise InquirerPy pour une expérience utilisateur optimale
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import colorama
from colorama import Fore, Back, Style

# Initialiser colorama pour Windows
colorama.init()

class SatelixCLI:
    """Interface CLI moderne pour Satelix"""

    def __init__(self):
        """Initialisation de l'interface"""
        self.clear_screen()
        self.show_banner()

    def clear_screen(self):
        """Nettoyer l'écran"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        """Afficher la bannière moderne"""
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                  🛰️  SATELIX AUTOMATION SUITE  🛰️               ║")
        print("║                         Version 2.0 Pro                     ║")
        print("║                      Interface Interactive                   ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✨ Interface moderne avec navigation au clavier{Style.RESET_ALL}")
        print()

    def show_main_menu(self):
        """Afficher le menu principal moderne"""
        choices = [
            Choice("setup", "🔧 Configuration initiale", enabled=True),
            Choice("create_today", "📦 Créer inventaires (aujourd'hui)", enabled=True),
            Choice("create_date", "📅 Créer inventaires (date spécifique)", enabled=True),
            Separator("─── AUTOMATISATION ───"),
            Choice("schedule", "⏰ Programmer exécution quotidienne", enabled=True),
            Separator("─── MAINTENANCE ───"),
            Choice("logs", "📋 Consulter les logs", enabled=True),
            Choice("cleanup", "🧹 Nettoyage des fichiers", enabled=True),
            Separator("─── DIAGNOSTIC ───"),
            Choice("diagnostic", "🔍 Diagnostic système", enabled=True),
            Choice("repair", "🔧 Réparation automatique", enabled=True),
            Choice("debug", "👁️  Mode debug (Chrome visible)", enabled=True),
            Separator("───────────────────"),
            Choice("quit", "🚪 Quitter", enabled=True),
        ]

        action = inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=choices,
            default="create_today",
            pointer="👉",
            instruction="(Utilisez ↑↓ pour naviguer, Entrée pour valider)"
        ).execute()

        return action

    def execute_action(self, action):
        """Exécuter l'action sélectionnée"""
        if action == "setup":
            self.setup_configuration()
        elif action == "create_today":
            self.create_inventories_today()
        elif action == "create_date":
            self.create_inventories_date()
        elif action == "schedule":
            self.setup_schedule()
        elif action == "logs":
            self.show_logs()
        elif action == "cleanup":
            self.cleanup_files()
        elif action == "diagnostic":
            self.run_diagnostic()
        elif action == "repair":
            self.run_repair()
        elif action == "debug":
            self.run_debug()
        elif action == "quit":
            self.quit_application()

    def setup_configuration(self):
        """Configuration initiale interactive"""
        self.clear_screen()
        print(f"{Fore.YELLOW}{Style.BRIGHT}🔧 CONFIGURATION INITIALE{Style.RESET_ALL}")
        print()

        # Vérifier si config existe
        env_file = Path("app/.env")
        if env_file.exists():
            reconfigure = inquirer.confirm(
                message="Une configuration existe déjà. La remplacer ?",
                default=False
            ).execute()

            if not reconfigure:
                print(f"{Fore.GREEN}Configuration conservée{Style.RESET_ALL}")
                self.wait_continue()
                return

        print(f"{Fore.CYAN}ℹ️  Collecte des informations de connexion Satelix{Style.RESET_ALL}")

        # URL Satelix
        url = inquirer.text(
            message="URL de connexion Satelix:",
            default="http://sql-industrie:7980/",
            validate=lambda x: len(x) > 0 or "URL requise"
        ).execute()

        # Nom d'utilisateur
        username = inquirer.text(
            message="Nom d'utilisateur Satelix:",
            validate=lambda x: len(x) > 0 or "Nom d'utilisateur requis"
        ).execute()

        # Mot de passe
        password = inquirer.secret(
            message="Mot de passe Satelix:",
            validate=lambda x: len(x) > 0 or "Mot de passe requis"
        ).execute()

        # Mode headless
        headless = inquirer.confirm(
            message="Exécution en arrière-plan (recommandé) ?",
            default=True
        ).execute()

        # Créer le fichier .env
        self.create_env_file(url, username, password, headless)

        # Test de connexion
        test_now = inquirer.confirm(
            message="Tester la connexion maintenant ?",
            default=True
        ).execute()

        if test_now:
            self.test_connection()

    def create_inventories_today(self):
        """Créer des inventaires pour aujourd'hui"""
        self.clear_screen()
        print(f"{Fore.BLUE}{Style.BRIGHT}📦 CRÉATION D'INVENTAIRES - AUJOURD'HUI{Style.RESET_ALL}")
        print()

        confirm = inquirer.confirm(
            message=f"Créer un inventaire pour le {datetime.now().strftime('%d/%m/%Y')} ?",
            default=True
        ).execute()

        if confirm:
            self.run_script("app\\update_today.bat")

    def create_inventories_date(self):
        """Créer des inventaires pour une date spécifique"""
        self.clear_screen()
        print(f"{Fore.BLUE}{Style.BRIGHT}📅 CRÉATION D'INVENTAIRES - DATE SPÉCIFIQUE{Style.RESET_ALL}")
        print()

        date_input = inquirer.text(
            message="Date cible (format JJ/MM/AAAA):",
            validate=self.validate_date,
            instruction="Exemple: 25/12/2025"
        ).execute()

        confirm = inquirer.confirm(
            message=f"Créer un inventaire pour le {date_input} ?",
            default=True
        ).execute()

        if confirm:
            self.run_script(f"app\\update_date.bat \"{date_input}\"")

    def setup_schedule(self):
        """Configuration de la planification"""
        self.clear_screen()
        print(f"{Fore.MAGENTA}{Style.BRIGHT}⏰ AUTOMATISATION QUOTIDIENNE{Style.RESET_ALL}")
        print()

        # Avertissement droits admin
        print(f"{Fore.YELLOW}⚠️  Cette fonctionnalité nécessite des droits administrateur{Style.RESET_ALL}")

        continue_setup = inquirer.confirm(
            message="Continuer la configuration ?",
            default=True
        ).execute()

        if continue_setup:
            time_choice = inquirer.select(
                message="Heure d'exécution quotidienne:",
                choices=[
                    Choice("08:00", "8h00 (recommandé)"),
                    Choice("07:30", "7h30"),
                    Choice("09:00", "9h00"),
                    Choice("custom", "Autre heure...")
                ],
                default="08:00"
            ).execute()

            if time_choice == "custom":
                time_choice = inquirer.text(
                    message="Heure personnalisée (format HH:MM):",
                    validate=self.validate_time
                ).execute()

            days = inquirer.checkbox(
                message="Jours d'exécution:",
                choices=[
                    Choice("MON", "Lundi", enabled=True),
                    Choice("TUE", "Mardi", enabled=True),
                    Choice("WED", "Mercredi", enabled=True),
                    Choice("THU", "Jeudi", enabled=True),
                    Choice("FRI", "Vendredi", enabled=True),
                    Choice("SAT", "Samedi", enabled=False),
                    Choice("SUN", "Dimanche", enabled=False),
                ],
                validate=lambda x: len(x) > 0 or "Sélectionnez au moins un jour"
            ).execute()

            print(f"\n{Fore.GREEN}Configuration:{Style.RESET_ALL}")
            print(f"⏰ Heure: {time_choice}")
            print(f"📅 Jours: {', '.join(days)}")

            confirm = inquirer.confirm(
                message="Appliquer cette configuration ?",
                default=True
            ).execute()

            if confirm:
                self.run_script("app\\setup_schedule.bat")

    def run_diagnostic(self):
        """Lancer le diagnostic"""
        self.clear_screen()
        print(f"{Fore.CYAN}{Style.BRIGHT}🔍 DIAGNOSTIC SYSTÈME{Style.RESET_ALL}")
        print()
        self.run_script("app\\diagnostic.bat")

    def run_repair(self):
        """Lancer les réparations automatiques"""
        self.clear_screen()
        print(f"{Fore.GREEN}{Style.BRIGHT}🔧 RÉPARATION AUTOMATIQUE{Style.RESET_ALL}")
        print()
        self.run_script("python app\\fix_connection.py")

    def run_debug(self):
        """Mode debug avec Chrome visible"""
        self.clear_screen()
        print(f"{Fore.RED}{Style.BRIGHT}👁️  MODE DEBUG{Style.RESET_ALL}")
        print()
        self.run_script("app\\debug_mode.bat")

    def show_logs(self):
        """Afficher les logs"""
        self.clear_screen()
        print(f"{Fore.WHITE}{Style.BRIGHT}📋 CONSULTATION DES LOGS{Style.RESET_ALL}")
        print()
        self.run_script("app\\show_logs.bat")

    def cleanup_files(self):
        """Nettoyage des fichiers"""
        self.clear_screen()
        print(f"{Fore.YELLOW}{Style.BRIGHT}🧹 NETTOYAGE DES FICHIERS{Style.RESET_ALL}")
        print()

        confirm = inquirer.confirm(
            message="Supprimer les fichiers de plus de 30 jours ?",
            default=True
        ).execute()

        if confirm:
            self.run_script("app\\cleanup.bat")

    def quit_application(self):
        """Quitter l'application"""
        self.clear_screen()
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                    👋 AU REVOIR !                         ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✨ Merci d'avoir utilisé Satelix Automation Suite{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Votre productivité vient d'augmenter !{Style.RESET_ALL}")
        print()
        sys.exit(0)

    def create_env_file(self, url, username, password, headless):
        """Créer le fichier .env"""
        env_content = f"""# Configuration Satelix Automation Suite
SATELIX_URL_LOGIN={url}
SATELIX_URL_INVENTAIRES={url}inventaire
SATELIX_USER={username}
SATELIX_PASSWORD={password}

# Configuration
HEADLESS={str(headless).lower()}
TIMEOUT=30
"""

        with open("app/.env", "w", encoding="utf-8") as f:
            f.write(env_content)

        print(f"{Fore.GREEN}✅ Configuration sauvegardée{Style.RESET_ALL}")

    def test_connection(self):
        """Tester la connexion"""
        print(f"{Fore.YELLOW}🔄 Test de connexion en cours...{Style.RESET_ALL}")
        self.run_script("python app\\diagnostic.py")

    def run_script(self, command):
        """Exécuter un script système"""
        try:
            result = subprocess.run(command, shell=True, cwd=Path.cwd())
            if result.returncode == 0:
                print(f"{Fore.GREEN}✅ Opération terminée avec succès{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Erreur lors de l'exécution (code: {result.returncode}){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur: {e}{Style.RESET_ALL}")

        self.wait_continue()

    def wait_continue(self):
        """Attendre avant de continuer"""
        inquirer.text(
            message="Appuyez sur Entrée pour continuer...",
            default=""
        ).execute()

    def validate_date(self, date_str):
        """Valider le format de date"""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return "Format invalide. Utilisez JJ/MM/AAAA"

    def validate_time(self, time_str):
        """Valider le format d'heure"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return "Format invalide. Utilisez HH:MM"

    def run(self):
        """Boucle principale de l'interface"""
        try:
            while True:
                action = self.show_main_menu()
                self.execute_action(action)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interruption utilisateur{Style.RESET_ALL}")
            self.quit_application()
        except Exception as e:
            print(f"\n{Fore.RED}Erreur inattendue: {e}{Style.RESET_ALL}")
            self.wait_continue()

def main():
    """Point d'entrée principal"""
    cli = SatelixCLI()
    cli.run()

if __name__ == "__main__":
    main()