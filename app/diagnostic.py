#!/usr/bin/env python3
"""
Outil de diagnostic pour résoudre les problèmes de connexion Satelix
"""

import os
import sys
import socket
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import time


class SatelixDiagnostic:
    """Diagnostic complet pour Satelix"""

    def __init__(self):
        """Initialisation du diagnostic"""
        load_dotenv('app/.env')

        self.login_url = os.getenv('SATELIX_URL_LOGIN')
        self.username = os.getenv('SATELIX_USER')
        self.password = os.getenv('SATELIX_PASSWORD')

        self.issues = []
        self.solutions = []

    def print_section(self, title):
        """Afficher une section de diagnostic"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")

    def print_result(self, test_name, success, details=""):
        """Afficher le résultat d'un test"""
        status = "✅ OK" if success else "❌ ERREUR"
        print(f"{status:8} {test_name}")
        if details:
            print(f"         {details}")

        if not success:
            self.issues.append(f"{test_name}: {details}")

    def test_configuration(self):
        """Test de la configuration"""
        self.print_section("TEST DE CONFIGURATION")

        # Test fichier .env
        env_exists = Path('app/.env').exists()
        self.print_result("Fichier .env", env_exists,
                         "Présent" if env_exists else "Manquant - Lancez la configuration [1]")

        if not env_exists:
            return False

        # Test variables obligatoires
        required_vars = {
            'SATELIX_URL_LOGIN': self.login_url,
            'SATELIX_USER': self.username,
            'SATELIX_PASSWORD': self.password
        }

        all_vars_ok = True
        for var_name, var_value in required_vars.items():
            var_ok = bool(var_value and var_value.strip())
            self.print_result(f"Variable {var_name}", var_ok,
                             "Définie" if var_ok else "Manquante ou vide")
            if not var_ok:
                all_vars_ok = False

        return all_vars_ok

    def test_network_connectivity(self):
        """Test de connectivité réseau"""
        self.print_section("TEST DE CONNECTIVITÉ RÉSEAU")

        if not self.login_url:
            self.print_result("URL Satelix", False, "URL non configurée")
            return False

        # Parser l'URL
        parsed = urlparse(self.login_url)
        host = parsed.hostname
        port = parsed.port or 80

        # Test DNS
        try:
            ip = socket.gethostbyname(host)
            self.print_result("Résolution DNS", True, f"{host} → {ip}")
            dns_ok = True
        except socket.gaierror:
            self.print_result("Résolution DNS", False, f"Impossible de résoudre {host}")
            self.solutions.append("Vérifiez que vous êtes connecté au réseau de l'entreprise")
            self.solutions.append("Essayez de remplacer 'sql-industrie' par l'adresse IP directe")
            dns_ok = False

        if not dns_ok:
            return False

        # Test connexion TCP
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()

            tcp_ok = result == 0
            self.print_result("Connexion TCP", tcp_ok,
                             f"Port {port} accessible" if tcp_ok else f"Port {port} fermé ou inaccessible")

            if not tcp_ok:
                self.solutions.append(f"Vérifiez que le service sur {host}:{port} est démarré")
                self.solutions.append("Contactez l'administrateur réseau")

        except Exception as e:
            self.print_result("Connexion TCP", False, str(e))
            tcp_ok = False

        return tcp_ok

    def test_http_access(self):
        """Test d'accès HTTP"""
        self.print_section("TEST D'ACCÈS HTTP")

        if not self.login_url:
            return False

        try:
            # Test GET simple
            response = requests.get(self.login_url, timeout=15, verify=False)

            status_ok = response.status_code == 200
            self.print_result("Accès HTTP", status_ok,
                             f"Code {response.status_code}" if not status_ok else "Page accessible")

            if not status_ok:
                if response.status_code == 404:
                    self.solutions.append("L'URL semble incorrecte (erreur 404)")
                elif response.status_code == 403:
                    self.solutions.append("Accès refusé - vérifiez les permissions")
                elif response.status_code >= 500:
                    self.solutions.append("Erreur serveur - contactez l'administrateur")

            # Test contenu de la page
            if status_ok:
                content = response.text.lower()
                has_login = any(term in content for term in ['login', 'connexion', 'mot de passe', 'utilisateur'])
                self.print_result("Page de connexion", has_login,
                                 "Formulaire de connexion détecté" if has_login else "Pas de formulaire trouvé")

                if not has_login:
                    self.solutions.append("L'URL ne semble pas pointer vers une page de connexion")

            return status_ok

        except requests.exceptions.ConnectTimeout:
            self.print_result("Accès HTTP", False, "Timeout de connexion")
            self.solutions.append("Le serveur met trop de temps à répondre")
            return False
        except requests.exceptions.ConnectionError:
            self.print_result("Accès HTTP", False, "Erreur de connexion")
            self.solutions.append("Impossible de se connecter au serveur web")
            return False
        except Exception as e:
            self.print_result("Accès HTTP", False, str(e))
            return False

    def test_selenium_requirements(self):
        """Test des prérequis Selenium"""
        self.print_section("TEST DES PRÉREQUIS SELENIUM")

        # Test Selenium
        try:
            import selenium
            self.print_result("Module Selenium", True, f"Version {selenium.__version__}")
        except ImportError:
            self.print_result("Module Selenium", False, "Module non installé")
            self.solutions.append("Installez Selenium: pip install selenium")
            return False

        # Test Chrome
        chrome_found = False
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', ''))
        ]

        for path in chrome_paths:
            if os.path.exists(path):
                self.print_result("Google Chrome", True, f"Trouvé: {path}")
                chrome_found = True
                break

        if not chrome_found:
            self.print_result("Google Chrome", False, "Chrome non trouvé")
            self.solutions.append("Installez Google Chrome depuis https://www.google.com/chrome/")

        # Test ChromeDriver
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')

            # Test rapide de création du driver
            driver = webdriver.Chrome(options=options)
            driver.get('about:blank')
            driver.quit()

            self.print_result("ChromeDriver", True, "Fonctionnel")
            return True

        except Exception as e:
            self.print_result("ChromeDriver", False, str(e))
            self.solutions.append("Problème avec ChromeDriver - réinstallez Chrome")
            return False

    def test_full_connection(self):
        """Test de connexion complète avec Selenium"""
        self.print_section("TEST DE CONNEXION COMPLÈTE")

        if not all([self.login_url, self.username, self.password]):
            self.print_result("Paramètres complets", False, "Configuration incomplète")
            return False

        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Configuration Chrome
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

            print("   🔍 Lancement du navigateur...")
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 30)

            try:
                # Chargement de la page
                print(f"   🔍 Chargement de {self.login_url}")
                driver.get(self.login_url)

                page_loaded = "satelix" in driver.title.lower() or len(driver.page_source) > 1000
                self.print_result("Chargement page", page_loaded,
                                 f"Titre: {driver.title[:50]}...")

                # Recherche des champs de connexion
                print("   🔍 Recherche des champs de connexion...")
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Utilisateur'], input[type='text'], input[name*='user']"))
                    )
                    self.print_result("Champ utilisateur", True, "Trouvé")
                except:
                    self.print_result("Champ utilisateur", False, "Non trouvé")
                    self.solutions.append("La page de connexion a peut-être changé")
                    return False

                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[placeholder*='mot de passe']")
                    self.print_result("Champ mot de passe", True, "Trouvé")
                except:
                    self.print_result("Champ mot de passe", False, "Non trouvé")
                    return False

                # Test de saisie
                print("   🔍 Test de saisie des identifiants...")
                username_field.clear()
                username_field.send_keys(self.username)
                password_field.clear()
                password_field.send_keys(self.password)

                self.print_result("Saisie identifiants", True, "Champs remplis")

                # Recherche du bouton de connexion
                login_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'connecter') or contains(text(), 'Connecter') or contains(text(), 'Se connecter')]")
                if not login_buttons:
                    login_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")

                if login_buttons:
                    self.print_result("Bouton connexion", True, f"{len(login_buttons)} bouton(s) trouvé(s)")

                    # Test de clic (sans vraiment se connecter avec les vrais identifiants)
                    print("   🔍 Simulation du clic de connexion...")
                    initial_url = driver.current_url
                    login_buttons[0].click()

                    # Attendre un changement (2 secondes max)
                    time.sleep(2)

                    # Vérifier s'il y a eu un changement
                    url_changed = driver.current_url != initial_url
                    error_messages = driver.find_elements(By.XPATH, "//*[contains(text(), 'erreur') or contains(text(), 'incorrect') or contains(text(), 'invalide')]")

                    if url_changed:
                        self.print_result("Réaction connexion", True, "Redirection détectée")
                    elif error_messages:
                        self.print_result("Réaction connexion", True, "Message d'erreur affiché (normal)")
                    else:
                        self.print_result("Réaction connexion", False, "Aucune réaction visible")

                else:
                    self.print_result("Bouton connexion", False, "Non trouvé")
                    self.solutions.append("Le bouton de connexion a peut-être changé")

                return True

            finally:
                driver.quit()

        except Exception as e:
            self.print_result("Test complet", False, str(e))
            self.solutions.append("Erreur lors du test complet - voir détails ci-dessus")
            return False

    def run_full_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                          DIAGNOSTIC SATELIX                                 ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")

        # Tests dans l'ordre
        tests = [
            ("Configuration", self.test_configuration),
            ("Connectivité réseau", self.test_network_connectivity),
            ("Accès HTTP", self.test_http_access),
            ("Prérequis Selenium", self.test_selenium_requirements),
            ("Connexion complète", self.test_full_connection)
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"\n❌ ERREUR lors du test '{test_name}': {e}")
                results[test_name] = False

        # Résumé
        self.print_section("RÉSUMÉ DU DIAGNOSTIC")

        success_count = sum(results.values())
        total_count = len(results)

        print(f"Tests réussis: {success_count}/{total_count}")

        if success_count == total_count:
            print("\n🎉 TOUS LES TESTS SONT OK !")
            print("Le problème peut venir des identifiants ou d'un changement récent de l'interface.")
        else:
            print(f"\n⚠️  {total_count - success_count} problème(s) détecté(s)")

        # Solutions proposées
        if self.solutions:
            self.print_section("SOLUTIONS PROPOSÉES")
            for i, solution in enumerate(self.solutions, 1):
                print(f"{i}. {solution}")

        return success_count == total_count


def main():
    """Point d'entrée principal"""
    diagnostic = SatelixDiagnostic()

    try:
        diagnostic.run_full_diagnostic()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrompu par l'utilisateur.")
    except Exception as e:
        print(f"\nErreur inattendue: {e}")

    print("\n" + "="*60)
    print("Diagnostic terminé. Appuyez sur Entrée pour continuer...")
    input()


if __name__ == "__main__":
    main()