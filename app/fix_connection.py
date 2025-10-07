#!/usr/bin/env python3
"""
Correctifs automatiques pour les problèmes de connexion Satelix
"""

import os
import sys
import socket
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse


class SatelixConnectionFixer:
    """Correctifs automatiques pour la connexion"""

    def __init__(self):
        """Initialisation"""
        load_dotenv('app/.env')
        self.login_url = os.getenv('SATELIX_URL_LOGIN')
        self.fixes_applied = []

    def print_section(self, title):
        """Afficher une section"""
        print(f"\n{'='*50}")
        print(f" {title}")
        print(f"{'='*50}")

    def fix_dns_resolution(self):
        """Tenter de corriger les problèmes DNS"""
        self.print_section("CORRECTION DNS")

        if not self.login_url:
            return False

        parsed = urlparse(self.login_url)
        host = parsed.hostname

        # Test de résolution DNS
        try:
            ip = socket.gethostbyname(host)
            print(f"✅ DNS OK: {host} → {ip}")
            return True
        except socket.gaierror:
            print(f"❌ Impossible de résoudre {host}")

            # Proposer des corrections
            if 'sql-industrie' in host:
                # Essayer des IPs communes d'entreprise
                test_ips = ['192.168.1.100', '192.168.0.100', '10.0.0.100', '172.16.0.100']

                print("🔧 Test d'adresses IP alternatives...")
                for test_ip in test_ips:
                    try:
                        # Test de connexion
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        result = sock.connect_ex((test_ip, 7980))
                        sock.close()

                        if result == 0:
                            print(f"✅ IP fonctionnelle trouvée: {test_ip}")

                            # Proposer le remplacement
                            new_url = self.login_url.replace(host, test_ip)
                            print(f"Nouvelle URL proposée: {new_url}")

                            response = input("Voulez-vous utiliser cette IP ? (o/n): ")
                            if response.lower() == 'o':
                                self.update_env_url(new_url)
                                self.fixes_applied.append(f"URL mise à jour vers {new_url}")
                                return True

                    except:
                        continue

            print("❌ Aucune correction DNS automatique trouvée")
            print("💡 Solutions manuelles:")
            print("   1. Vérifiez votre connexion au réseau d'entreprise")
            print("   2. Contactez l'IT pour obtenir la bonne adresse IP")
            print("   3. Utilisez un VPN si nécessaire")

            return False

    def fix_url_format(self):
        """Corriger le format de l'URL"""
        self.print_section("CORRECTION FORMAT URL")

        if not self.login_url:
            print("❌ Aucune URL configurée")
            return False

        original_url = self.login_url
        fixed_url = original_url

        # Corrections communes
        corrections = [
            # Ajouter http:// si manquant
            lambda url: f"http://{url}" if not url.startswith(('http://', 'https://')) else url,

            # Corriger le port
            lambda url: url.replace(':80/', ':7980/') if ':80/' in url else url,

            # Assurer le slash final
            lambda url: url if url.endswith('/') else f"{url}/",

            # Corriger les doubles slashes
            lambda url: url.replace('///', '//')
        ]

        for correction in corrections:
            new_url = correction(fixed_url)
            if new_url != fixed_url:
                print(f"🔧 Correction: {fixed_url} → {new_url}")
                fixed_url = new_url

        if fixed_url != original_url:
            print(f"✅ URL corrigée: {original_url} → {fixed_url}")

            response = input("Appliquer cette correction ? (o/n): ")
            if response.lower() == 'o':
                self.update_env_url(fixed_url)
                self.fixes_applied.append(f"Format URL corrigé")
                return True

        else:
            print("✅ Format URL correct")

        return True

    def test_alternative_ports(self):
        """Tester des ports alternatifs"""
        self.print_section("TEST PORTS ALTERNATIFS")

        if not self.login_url:
            return False

        parsed = urlparse(self.login_url)
        host = parsed.hostname

        # Tester la résolution DNS d'abord
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            print(f"❌ Impossible de résoudre {host} - correction DNS nécessaire d'abord")
            return False

        # Ports à tester
        test_ports = [7980, 8080, 80, 443, 8000, 9090]
        current_port = parsed.port or 80

        print(f"Port actuel: {current_port}")

        for port in test_ports:
            if port == current_port:
                continue

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    print(f"✅ Port {port} accessible")

                    # Test HTTP
                    test_url = f"http://{host}:{port}/"
                    try:
                        response = requests.get(test_url, timeout=5)
                        if response.status_code == 200:
                            print(f"🌐 Service web fonctionnel sur le port {port}")

                            response_input = input(f"Utiliser le port {port} ? (o/n): ")
                            if response_input.lower() == 'o':
                                new_url = f"http://{host}:{port}/"
                                self.update_env_url(new_url)
                                self.fixes_applied.append(f"Port changé vers {port}")
                                return True
                    except:
                        print(f"⚠️  Port {port} ouvert mais pas de service web")

                else:
                    print(f"❌ Port {port} fermé")

            except Exception as e:
                print(f"❌ Erreur test port {port}: {e}")

        return False

    def update_env_url(self, new_url):
        """Mettre à jour l'URL dans le fichier .env"""
        env_file = Path('app/.env')

        if not env_file.exists():
            print("❌ Fichier .env non trouvé")
            return False

        # Lire le fichier
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Modifier les lignes URL
        modified = False
        for i, line in enumerate(lines):
            if line.startswith('SATELIX_URL_LOGIN='):
                lines[i] = f"SATELIX_URL_LOGIN={new_url}\n"
                modified = True
            elif line.startswith('SATELIX_URL_INVENTAIRES='):
                inventaires_url = new_url.rstrip('/') + '/inventaire'
                lines[i] = f"SATELIX_URL_INVENTAIRES={inventaires_url}\n"
                modified = True

        if modified:
            # Sauvegarder
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print("✅ Configuration mise à jour")
            return True

        return False

    def run_fixes(self):
        """Exécuter tous les correctifs"""
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                    CORRECTIFS AUTOMATIQUES SATELIX                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")

        fixes = [
            ("Format URL", self.fix_url_format),
            ("Résolution DNS", self.fix_dns_resolution),
            ("Ports alternatifs", self.test_alternative_ports)
        ]

        for fix_name, fix_func in fixes:
            print(f"\n🔧 Application du correctif: {fix_name}")
            try:
                success = fix_func()
                if success:
                    print(f"✅ Correctif '{fix_name}' appliqué")
                else:
                    print(f"❌ Correctif '{fix_name}' non applicable")
            except Exception as e:
                print(f"❌ Erreur lors du correctif '{fix_name}': {e}")

        # Résumé
        print("\n" + "="*60)
        print(" RÉSUMÉ DES CORRECTIFS")
        print("="*60)

        if self.fixes_applied:
            print("✅ Correctifs appliqués:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")

            print("\n💡 Relancez maintenant le test de connexion [2] pour vérifier.")

        else:
            print("❌ Aucun correctif automatique n'a pu être appliqué.")
            print("\n💡 Solutions manuelles:")
            print("   1. Vérifiez votre connexion réseau d'entreprise")
            print("   2. Contactez votre administrateur IT")
            print("   3. Vérifiez que Satelix est démarré sur le serveur")

        return len(self.fixes_applied) > 0


def main():
    """Point d'entrée principal"""
    fixer = SatelixConnectionFixer()

    try:
        fixer.run_fixes()
    except KeyboardInterrupt:
        print("\n\nCorrectifs interrompus par l'utilisateur.")
    except Exception as e:
        print(f"\nErreur inattendue: {e}")

    print("\n" + "="*60)
    print("Correctifs terminés. Appuyez sur Entrée pour continuer...")
    input()


if __name__ == "__main__":
    main()