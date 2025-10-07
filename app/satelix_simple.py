#!/usr/bin/env python3
"""
Script d'automatisation RPA pour mise à jour des dates d'inventaires Satelix
Modifie la date d'inventaires existants et les actualise automatiquement
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys


class SatelixInventoryDateUpdater:
    """Classe principale pour la mise à jour des dates d'inventaires Satelix"""

    def __init__(self, target_date=None):
        """Initialisation avec date cible optionnelle"""
        # Chargement du fichier .env
        load_dotenv()

        # Configuration des logs
        self.setup_logging()

        # Variables d'environnement (obligatoires)
        self.login_url = os.getenv('SATELIX_URL_LOGIN')
        self.inventaires_url = os.getenv('SATELIX_URL_INVENTAIRES')
        self.username = os.getenv('SATELIX_USER')
        self.password = os.getenv('SATELIX_PASSWORD')

        # Configuration
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.timeout = int(os.getenv('TIMEOUT', '30'))

        # Driver Selenium
        self.driver = None
        self.wait = None

        # Date cible (par défaut: aujourd'hui)
        if target_date:
            if isinstance(target_date, str):
                self.target_date = datetime.strptime(target_date, '%d/%m/%Y')
            else:
                self.target_date = target_date
        else:
            self.target_date = datetime.now()

        self.target_date_str = self.target_date.strftime('%d/%m/%Y')

        self.logger.info("Initialisation terminée - Date cible: %s", self.target_date_str)

    def setup_logging(self):
        """Configuration du système de logging"""
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / 'satelix_update_inventory_dates.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

    def validate_environment(self):
        """Validation des variables d'environnement obligatoires"""
        required_vars = [
            ('SATELIX_URL_LOGIN', self.login_url),
            ('SATELIX_URL_INVENTAIRES', self.inventaires_url),
            ('SATELIX_USER', self.username),
            ('SATELIX_PASSWORD', self.password)
        ]

        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            self.logger.error("Variables d'environnement manquantes: %s", ', '.join(missing_vars))
            return False

        self.logger.info("Toutes les variables d'environnement obligatoires sont présentes")
        return True

    def setup_driver(self):
        """Configuration et initialisation du driver Chrome"""
        try:
            options = Options()

            if self.headless:
                options.add_argument('--headless=new')
                self.logger.info("Mode headless activé")

            # Options pour environnement serveur
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, self.timeout)

            self.logger.info("Driver Chrome initialisé avec succès")
            return True

        except WebDriverException as e:
            self.logger.error("Erreur lors de l'initialisation du driver Chrome: %s", str(e))
            return False

    def take_screenshot(self, name):
        """Prendre une capture d'écran et la sauvegarder"""
        try:
            logs_dir = Path('logs')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = logs_dir / f"{name}_{timestamp}.png"

            self.driver.save_screenshot(str(screenshot_path))
            self.logger.info("Capture d'écran sauvegardée: %s", screenshot_path)
            return str(screenshot_path)

        except Exception as e:
            self.logger.error("Erreur lors de la capture d'écran: %s", str(e))
            return None

    def login(self):
        """Connexion à Satelix"""
        try:
            self.logger.info("Début de la connexion à Satelix")
            self.driver.get(self.login_url)

            # Champs de connexion Satelix
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Utilisateur / adresse mail']"))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Mot de passe']")

            # Bouton de connexion
            login_button = None
            selectors = [
                (By.XPATH, "//button[contains(text(), 'Se connecter')]"),
                (By.XPATH, "//*[contains(text(), 'Se connecter')]"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button")
            ]

            for by_type, selector in selectors:
                try:
                    login_button = self.driver.find_element(by_type, selector)
                    if login_button:
                        self.logger.info("Bouton de connexion trouvé avec: %s = %s", by_type, selector)
                        break
                except NoSuchElementException:
                    continue

            if not login_button:
                raise NoSuchElementException("Aucun bouton de connexion trouvé")

            # Saisie des identifiants
            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)

            self.take_screenshot("before_login")
            login_button.click()

            # Attendre la connexion - chercher des éléments spécifiques à l'interface connectée
            self.wait.until(
                EC.any_of(
                    # Chercher le nom d'utilisateur affiché (GEOFFROY)
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'GEOFFROY')]")),
                    # Chercher des éléments du menu principal
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Inventaire')]")),
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Dossier')]")),
                    # Chercher la sidebar de navigation
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar, nav, [role='navigation']")),
                    # Chercher des éléments spécifiques vus dans la capture
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Écarts de stock')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Tableau de bord')]"))
                )
            )

            self.take_screenshot("after_login")
            self.logger.info("Connexion réussie")
            return True

        except Exception as e:
            self.logger.error("Erreur lors de la connexion: %s", str(e))
            self.take_screenshot("login_error")
            return False

    def navigate_to_inventaires(self):
        """Navigation vers la page Inventaires"""
        try:
            self.logger.info("Navigation vers la page Inventaires")
            self.driver.get(self.inventaires_url)

            # Attendre le chargement de la page
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Inventaire')]")),
                    EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Nouvelle capture')]")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'inventaire')]"))
                )
            )

            self.take_screenshot("inventaires_page")
            self.logger.info("Page Inventaires chargée avec succès")
            return True

        except Exception as e:
            self.logger.error("Erreur lors de la navigation vers Inventaires: %s", str(e))
            self.take_screenshot("navigation_error")
            return False

    def find_existing_inventories(self):
        """Rechercher les inventaires existants"""
        try:
            self.logger.info("Recherche des inventaires existants")
            inventories = []

            # Stratégie 1: Table HTML principale
            try:
                table_rows = self.driver.find_elements(By.CSS_SELECTOR, "table tr")
                for i, row in enumerate(table_rows):
                    if i == 0:  # Skip header
                        continue

                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    if cells and len(cells) > 1:
                        # Chercher une date dans les cellules
                        date_cell = None
                        action_button = None

                        for cell in cells:
                            cell_text = cell.text.strip()
                            if '/' in cell_text and len(cell_text) == 10:  # Format DD/MM/YYYY
                                try:
                                    inventory_date = datetime.strptime(cell_text, '%d/%m/%Y')
                                    date_cell = cell

                                    # Chercher le bouton d'action dans la même ligne
                                    try:
                                        action_button = row.find_element(By.CSS_SELECTOR, "button, a.btn, .btn, [class*='btn']")
                                    except:
                                        pass

                                    inventories.append({
                                        'date': inventory_date,
                                        'date_str': cell_text,
                                        'row_element': row,
                                        'date_element': date_cell,
                                        'action_button': action_button
                                    })
                                    self.logger.info("Inventaire trouvé: %s", cell_text)
                                    break
                                except ValueError:
                                    continue
            except NoSuchElementException:
                pass

            # Stratégie 2: Recherche dans toutes les tables de la page
            try:
                all_tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
                for table in all_tables:
                    if table not in [row.find_element(By.XPATH, ".//ancestor::table") for inv in inventories for row in [inv.get('row_element')] if row]:
                        rows = table.find_elements(By.CSS_SELECTOR, "tr")
                        for row in rows:
                            cells = row.find_elements(By.CSS_SELECTOR, "td")
                            for cell in cells:
                                cell_text = cell.text.strip()
                                if '/' in cell_text and len(cell_text) == 10:
                                    try:
                                        inventory_date = datetime.strptime(cell_text, '%d/%m/%Y')
                                        # Vérifier qu'on n'a pas déjà cet inventaire
                                        if not any(inv['date_str'] == cell_text for inv in inventories):
                                            inventories.append({
                                                'date': inventory_date,
                                                'date_str': cell_text,
                                                'row_element': row,
                                                'date_element': cell,
                                                'action_button': None
                                            })
                                            self.logger.info("Inventaire trouvé dans table secondaire: %s", cell_text)
                                        break
                                    except ValueError:
                                        continue
            except:
                pass

            # Stratégie 3: Recherche de cartes ou divs d'inventaires
            try:
                inventory_cards = self.driver.find_elements(By.CSS_SELECTOR, ".card, .panel, .inventory-item, [class*='inventaire']")
                for card in inventory_cards:
                    card_text = card.text
                    # Recherche de dates dans le texte de la carte
                    import re
                    dates = re.findall(r'\b(\d{2}/\d{2}/\d{4})\b', card_text)
                    for date_str in dates:
                        try:
                            inventory_date = datetime.strptime(date_str, '%d/%m/%Y')
                            # Vérifier qu'on n'a pas déjà cet inventaire
                            if not any(inv['date_str'] == date_str for inv in inventories):
                                inventories.append({
                                    'date': inventory_date,
                                    'date_str': date_str,
                                    'row_element': card,
                                    'date_element': card,
                                    'action_button': None
                                })
                                self.logger.info("Inventaire trouvé dans carte: %s", date_str)
                        except ValueError:
                            continue
            except:
                pass

            # Stratégie 2: Recherche de liens ou boutons d'édition
            try:
                edit_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'edit') or contains(text(), 'Modifier') or contains(text(), 'Éditer')]")
                action_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Modifier') or contains(text(), 'Éditer') or contains(text(), 'Mettre à jour')]")

                for element in edit_links + action_buttons:
                    # Chercher une date dans le même contexte (parent, siblings)
                    parent = element.find_element(By.XPATH, "..")
                    if parent:
                        date_match = self._extract_date_from_text(parent.text)
                        if date_match:
                            inventories.append({
                                'date': date_match,
                                'date_str': date_match.strftime('%d/%m/%Y'),
                                'edit_element': element
                            })
                            self.logger.info("Inventaire modifiable trouvé: %s", date_match.strftime('%d/%m/%Y'))
            except:
                pass

            self.logger.info("Total inventaires trouvés: %d", len(inventories))
            return inventories

        except Exception as e:
            self.logger.error("Erreur lors de la recherche d'inventaires: %s", str(e))
            return []

    def _extract_date_from_text(self, text):
        """Extraire une date au format DD/MM/YYYY d'un texte"""
        import re
        date_pattern = r'\b(\d{2}/\d{2}/\d{4})\b'
        match = re.search(date_pattern, text)
        if match:
            try:
                return datetime.strptime(match.group(1), '%d/%m/%Y')
            except ValueError:
                return None
        return None

    def create_new_inventory(self, template_inventory=None):
        """Créer un nouvel inventaire basé sur un inventaire existant"""
        try:
            self.logger.info("Création d'un nouvel inventaire avec la date %s", self.target_date_str)

            # Attendre que les modals/spinners disparaissent
            import time
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.ID, "modalSpinner"))
                )
            except:
                pass

            # Cliquer sur le bouton + pour créer un nouvel inventaire
            create_button_selectors = [
                "button[title*='Nouvel']",  # Bouton avec titre contenant "Nouvel"
                "a[title*='Nouvel']",  # Lien avec titre contenant "Nouvel"
                ".btn-success",  # Boutons verts
                ".btn-primary",  # Boutons bleus
                "button.btn",  # Tous les boutons
                "a.btn"  # Tous les liens-boutons
            ]

            create_button = None
            for selector in create_button_selectors:
                try:
                    create_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if create_button.is_displayed() and create_button.is_enabled():
                        self.logger.info(f"Bouton de création trouvé: {selector}")
                        break
                except:
                    continue

            # Si pas trouvé par CSS, essayer par position (bouton vert en haut à droite)
            if not create_button:
                try:
                    # Chercher tous les boutons verts
                    green_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn-success, .btn-primary")
                    for button in green_buttons:
                        if button.is_displayed() and button.is_enabled():
                            # Vérifier si c'est dans la zone en haut à droite
                            location = button.location
                            if location['x'] > 1000:  # Approximation pour côté droit
                                create_button = button
                                self.logger.info("Bouton de création trouvé par position")
                                break
                except:
                    pass

            if not create_button:
                self.logger.error("Impossible de trouver le bouton de création d'inventaire")
                return False

            # Cliquer sur le bouton de création
            self.driver.execute_script("arguments[0].scrollIntoView();", create_button)
            time.sleep(1)
            create_button.click()
            self.logger.info("Bouton de création cliqué")

            # Attendre l'ouverture du formulaire de création
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-body")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='date']")),
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'date')]"))
                )
            )
            self.logger.info("Formulaire de création ouvert")

            time.sleep(2)  # Attendre le chargement complet

            # D'abord, faire défiler vers le haut du formulaire pour voir tous les champs
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            # Prendre une capture d'écran du haut du formulaire
            self.take_screenshot("top_of_form")

            # Remplir le formulaire avec les données du template (si fourni) et la nouvelle date
            if template_inventory:
                self.logger.info("Copie des paramètres depuis l'inventaire template")
                # Copier les champs si possible (titre, dépôt, etc.)
                self._fill_inventory_form_from_template(template_inventory)

            # Définir la date d'inventaire
            date_set = self._set_inventory_date()

            if not date_set:
                self.logger.error("Impossible de définir la date d'inventaire")
                return False

            # Sauvegarder le nouvel inventaire
            save_success = self._save_new_inventory()

            if save_success:
                self.logger.info("Nouvel inventaire créé avec succès")
                return True
            else:
                self.logger.error("Échec de la création du nouvel inventaire")
                return False

        except Exception as e:
            self.logger.error("Erreur lors de la création d'inventaire: %s", str(e))
            self.take_screenshot("create_inventory_error")
            return False

    def _fill_inventory_form_from_template(self, template_inventory):
        """Remplir le formulaire avec toutes les données spécifiées"""
        try:
            import time

            # 1. Définir l'intitulé: "Inventaire filtres"
            self.logger.info("📝 Définition de l'intitulé: Inventaire filtres")
            self._fill_form_field("intitule", "Inventaire filtres")
            time.sleep(1)

            # 2. Sélectionner "DEPOT" dans le champ dépôts
            self.logger.info("🏢 Sélection du dépôt: DEPOT")
            self._select_dropdown_option("depot", "DEPOT")
            time.sleep(1)

            # 3. Sélectionner "CMUP" dans type de valorisation
            self.logger.info("💰 Sélection du type de valorisation: CMUP")
            self._select_dropdown_option("valorisation", "CMUP")
            time.sleep(1)

            # 4. Cocher "prix lot/série"
            self.logger.info("🔢 Cochage de 'prix lot/série'")
            self._check_specific_checkbox("prix lot/série", ["prix", "lot", "série"])
            time.sleep(1)

            # 5. Cocher "capture des stocks"
            self.logger.info("📦 Cochage de 'capture des stocks'")
            self._check_specific_checkbox("capture des stocks", ["capture", "stock"])
            time.sleep(1)

        except Exception as e:
            self.logger.warning("Impossible de remplir le formulaire: %s", str(e))

    def _fill_form_field(self, field_type, value):
        """Remplir un champ texte du formulaire"""
        try:
            self.logger.info(f"Recherche du champ {field_type}...")

            # Prendre une capture d'écran pour débugger
            self.take_screenshot(f"searching_{field_type}")

            # Pour l'intitulé, recherche exhaustive
            if field_type == "intitule":
                # Sélecteurs CSS très larges pour l'intitulé
                css_selectors = [
                    "input[name*='intitule']", "input[name*='titre']", "input[name*='nom']", "input[name*='title']",
                    "input[id*='intitule']", "input[id*='titre']", "input[id*='nom']", "input[id*='title']",
                    "input[placeholder*='intitule']", "input[placeholder*='titre']", "input[placeholder*='nom']",
                    "input[class*='intitule']", "input[class*='titre']", "input[class*='nom']"
                ]

                # Sélecteurs XPath pour l'intitulé
                xpath_selectors = [
                    "//input[contains(@name, 'intitule')]", "//input[contains(@name, 'titre')]",
                    "//input[contains(@name, 'nom')]", "//input[contains(@name, 'title')]",
                    "//input[contains(@id, 'intitule')]", "//input[contains(@id, 'titre')]",
                    "//input[contains(@id, 'nom')]", "//input[contains(@id, 'title')]",
                    "//input[contains(@placeholder, 'intitule')]", "//input[contains(@placeholder, 'titre')]",
                    "//input[contains(@placeholder, 'nom')]",
                    # Recherche par labels associés
                    "//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'intitule')]/..//input",
                    "//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'titre')]/..//input",
                    "//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'nom')]/..//input"
                ]

                all_selectors = css_selectors + xpath_selectors

            else:
                # Pour autres champs
                all_selectors = [f"input[name*='{field_type}']", f"input[id*='{field_type}']"]

            # Essayer tous les sélecteurs
            for selector in all_selectors:
                try:
                    if selector.startswith("//"):
                        fields = self.driver.find_elements(By.XPATH, selector)
                    else:
                        fields = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for field in fields:
                        if field.is_displayed() and field.is_enabled():
                            field_name = field.get_attribute('name') or ""
                            field_id = field.get_attribute('id') or ""
                            field_placeholder = field.get_attribute('placeholder') or ""

                            self.logger.info(f"Champ trouvé: name='{field_name}', id='{field_id}', placeholder='{field_placeholder}'")

                            # Scroll vers le champ
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                            import time
                            time.sleep(0.5)

                            # Remplir le champ
                            field.clear()
                            field.send_keys(value)

                            # Vérifier que la valeur a été saisie
                            time.sleep(0.5)
                            actual_value = field.get_attribute('value')
                            if actual_value == value:
                                self.logger.info(f"SUCCÈS! Champ {field_type} rempli avec: '{value}'")
                                return True
                            else:
                                self.logger.warning(f"Valeur partiellement saisie: '{actual_value}' au lieu de '{value}'")
                                # Essayer à nouveau
                                field.clear()
                                time.sleep(0.2)
                                field.send_keys(value)
                                time.sleep(0.5)
                                actual_value = field.get_attribute('value')
                                if actual_value == value:
                                    self.logger.info(f"SUCCÈS au 2e essai! Champ {field_type} rempli avec: '{value}'")
                                    return True

                except Exception as e:
                    self.logger.debug(f"Erreur avec sélecteur {selector}: {e}")
                    continue

            # Si pas trouvé, chercher TOUS les inputs de type text
            self.logger.warning(f"Recherche spécifique échouée, examen de tous les inputs text...")
            try:
                all_text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or not(@type)]")
                for i, field in enumerate(all_text_inputs):
                    if field.is_displayed() and field.is_enabled():
                        field_info = {
                            'name': field.get_attribute('name') or "",
                            'id': field.get_attribute('id') or "",
                            'placeholder': field.get_attribute('placeholder') or "",
                            'class': field.get_attribute('class') or ""
                        }
                        self.logger.info(f"Input {i+1}: {field_info}")

                        # Si c'est le premier input visible et qu'on cherche l'intitulé
                        if field_type == "intitule" and i == 0:
                            self.logger.info("Tentative avec le premier input trouvé...")
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                            time.sleep(0.5)
                            field.clear()
                            field.send_keys(value)
                            time.sleep(0.5)
                            if field.get_attribute('value') == value:
                                self.logger.info(f"SUCCÈS avec premier input! {field_type} = '{value}'")
                                return True

            except Exception as e:
                self.logger.error(f"Erreur lors de l'examen exhaustif: {e}")

            self.logger.error(f"ÉCHEC: Impossible de trouver le champ {field_type}")
            return False

        except Exception as e:
            self.logger.error(f"Erreur lors du remplissage du champ {field_type}: {e}")
        return False

    def _select_dropdown_option(self, dropdown_type, option_value):
        """Sélectionner une option dans un dropdown"""
        try:
            # Sélecteurs pour différents types de dropdowns
            dropdown_selectors = {
                "depot": [
                    "select[name*='depot']", "select[id*='depot']",
                    "select[name*='location']", "select[id*='location']"
                ],
                "valorisation": [
                    "select[name*='valorisation']", "select[id*='valorisation']",
                    "select[name*='valuation']", "select[id*='valuation']",
                    "select[name*='type']", "select[id*='type']"
                ]
            }

            selectors = dropdown_selectors.get(dropdown_type, [f"select[name*='{dropdown_type}']", f"select[id*='{dropdown_type}']"])

            for selector in selectors:
                try:
                    dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        from selenium.webdriver.support.ui import Select
                        select = Select(dropdown)

                        # Essayer de trouver l'option exacte
                        for option in select.options:
                            if option_value.upper() in option.text.upper():
                                select.select_by_visible_text(option.text)
                                self.logger.info(f"✅ Option '{option.text}' sélectionnée dans {dropdown_type}")
                                return True

                        # Si pas trouvé exactement, essayer par valeur
                        try:
                            select.select_by_value(option_value)
                            self.logger.info(f"✅ Option '{option_value}' sélectionnée par valeur dans {dropdown_type}")
                            return True
                        except:
                            pass

                except:
                    continue

            # Essayer avec XPath si CSS échoue
            xpath_selectors = [
                f"//select[contains(@name, '{dropdown_type}')]",
                f"//select[contains(@id, '{dropdown_type}')]"
            ]

            for selector in xpath_selectors:
                try:
                    dropdown = self.driver.find_element(By.XPATH, selector)
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        from selenium.webdriver.support.ui import Select
                        select = Select(dropdown)

                        for option in select.options:
                            if option_value.upper() in option.text.upper():
                                select.select_by_visible_text(option.text)
                                self.logger.info(f"✅ Option '{option.text}' sélectionnée dans {dropdown_type}")
                                return True
                except:
                    continue

            self.logger.warning(f"❌ Dropdown {dropdown_type} ou option {option_value} non trouvé(e)")
            return False

        except Exception as e:
            self.logger.error(f"Erreur lors de la sélection de {dropdown_type}: {e}")
            return False

    def _check_specific_checkbox(self, checkbox_name, keywords):
        """Cocher une checkbox spécifique basée sur des mots-clés"""
        try:
            self.logger.info(f"🔍 Recherche de la checkbox: {checkbox_name}")

            # Méthode 1: Recherche par label contenant les mots-clés
            for keyword in keywords:
                label_selectors = [
                    f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]",
                    f"//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]"
                ]

                for selector in label_selectors:
                    try:
                        labels = self.driver.find_elements(By.XPATH, selector)
                        for label in labels:
                            if label.is_displayed():
                                # Chercher la checkbox associée
                                try:
                                    checkbox = label.find_element(By.XPATH, ".//input[@type='checkbox']")
                                    if not checkbox.is_selected():
                                        checkbox.click()
                                        self.logger.info(f"✅ Checkbox '{checkbox_name}' cochée via label")
                                        return True
                                    else:
                                        self.logger.info(f"✅ Checkbox '{checkbox_name}' déjà cochée")
                                        return True
                                except:
                                    # Essayer de cliquer sur le label lui-même
                                    try:
                                        label.click()
                                        self.logger.info(f"✅ Checkbox '{checkbox_name}' cochée via clic sur label")
                                        return True
                                    except:
                                        pass
                    except:
                        continue

            # Méthode 2: Recherche de checkboxes avec attributs contenant les mots-clés
            for keyword in keywords:
                checkbox_selectors = [
                    f"//input[@type='checkbox'][contains(@name, '{keyword.lower()}')]",
                    f"//input[@type='checkbox'][contains(@id, '{keyword.lower()}')]"
                ]

                for selector in checkbox_selectors:
                    try:
                        checkboxes = self.driver.find_elements(By.XPATH, selector)
                        for checkbox in checkboxes:
                            if checkbox.is_displayed() and checkbox.is_enabled():
                                if not checkbox.is_selected():
                                    checkbox.click()
                                    self.logger.info(f"✅ Checkbox '{checkbox_name}' cochée par attribut")
                                    return True
                                else:
                                    self.logger.info(f"✅ Checkbox '{checkbox_name}' déjà cochée")
                                    return True
                    except:
                        continue

            # Méthode 3: Recherche exhaustive dans le contexte
            try:
                all_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                for checkbox in all_checkboxes:
                    if checkbox.is_displayed() and checkbox.is_enabled():
                        # Examiner le contexte autour de la checkbox
                        try:
                            parent = checkbox.find_element(By.XPATH, "..")
                            context_text = parent.text.lower()

                            # Vérifier si tous les mots-clés sont présents dans le contexte
                            if all(keyword.lower() in context_text for keyword in keywords):
                                if not checkbox.is_selected():
                                    checkbox.click()
                                    self.logger.info(f"✅ Checkbox '{checkbox_name}' cochée par contexte: {context_text[:50]}...")
                                    return True
                                else:
                                    self.logger.info(f"✅ Checkbox '{checkbox_name}' déjà cochée")
                                    return True
                        except:
                            continue
            except:
                pass

            self.logger.warning(f"❌ Checkbox '{checkbox_name}' non trouvée")
            return False

        except Exception as e:
            self.logger.error(f"Erreur lors du cochage de '{checkbox_name}': {e}")
            return False

    def _set_inventory_date(self):
        """Définir la date d'inventaire dans le formulaire"""
        try:
            import time
            # Rechercher le champ de date
            date_selectors = [
                "input[type='date']",
                "input[name*='date']",
                "input[id*='date']",
                "input[placeholder*='date']",
                "input[class*='date']"
            ]

            date_field = None
            for selector in date_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for field in fields:
                        if field.is_displayed() and field.is_enabled():
                            date_field = field
                            self.logger.info(f"Champ de date trouvé: {selector}")
                            break
                    if date_field:
                        break
                except:
                    continue

            if not date_field:
                self.logger.error("Champ de date non trouvé dans le formulaire")
                return False

            # Remplir la date
            date_field.clear()
            time.sleep(0.5)

            if date_field.get_attribute('type') == 'date':
                # Format ISO pour les champs date HTML5
                iso_date = self.target_date.strftime('%Y-%m-%d')
                date_field.send_keys(iso_date)
                self.logger.info(f"Date définie (ISO): {iso_date}")
            else:
                # Format DD/MM/YYYY pour les champs texte
                date_field.send_keys(self.target_date_str)
                self.logger.info(f"Date définie (FR): {self.target_date_str}")

            time.sleep(1)
            return True

        except Exception as e:
            self.logger.error("Erreur lors de la définition de la date: %s", str(e))
            return False

    def _save_new_inventory(self):
        """Sauvegarder le nouvel inventaire avec le bouton vert 'Ajouter'"""
        try:
            import time

            # Prendre une capture d'écran avant de chercher le bouton
            self.take_screenshot("before_save_button_search")

            # Rechercher spécifiquement le bouton vert "Ajouter" en bas
            save_selectors = [
                # Bouton "Ajouter" spécifiquement
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ajouter')]",
                # Boutons verts en bas de page
                "//button[contains(@class, 'btn-success')][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ajouter')]",
                # Autres variantes pour "Ajouter"
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'créer')]",
                "//input[@type='submit'][contains(@value, 'Ajouter')]",
                "//button[@type='submit'][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ajouter')]",
                # Boutons de type submit en général
                "//button[@type='submit']",
                "//input[@type='submit']",
                # Boutons verts (btn-success)
                "//button[contains(@class, 'btn-success')]",
                # Boutons primaires
                "//button[contains(@class, 'btn-primary')]"
            ]

            save_button = None
            self.logger.info("Recherche du bouton 'Ajouter' vert...")

            for i, selector in enumerate(save_selectors):
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    self.logger.info(f"Sélecteur {i+1}: {selector} - {len(buttons)} bouton(s) trouvé(s)")

                    for j, button in enumerate(buttons):
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.strip()
                            button_class = button.get_attribute('class') or ""
                            button_type = button.get_attribute('type') or ""

                            self.logger.info(f"  Bouton {j+1}: '{button_text}' - class='{button_class}' - type='{button_type}'")

                            # Priorité pour les boutons contenant "ajouter"
                            if 'ajouter' in button_text.lower():
                                save_button = button
                                self.logger.info(f"✅ Bouton 'Ajouter' sélectionné: '{button_text}'")
                                break
                            # Sinon, accepter les boutons verts ou de type submit
                            elif 'btn-success' in button_class or button_type == 'submit':
                                if not save_button:  # Prendre le premier si pas encore trouvé
                                    save_button = button
                                    self.logger.info(f"⚠️ Bouton de sauvegarde sélectionné: '{button_text}'")

                    if save_button and 'ajouter' in save_button.text.lower():
                        break  # Sortir si on a trouvé un bouton "ajouter"

                except Exception as e:
                    self.logger.warning(f"Erreur avec sélecteur {selector}: {e}")
                    continue

            if not save_button:
                self.logger.error("❌ Aucun bouton de sauvegarde trouvé")
                self.take_screenshot("no_save_button_found")
                return False

            # Scroll vers le bouton pour s'assurer qu'il est visible
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            time.sleep(1)

            # Cliquer sur le bouton de sauvegarde
            self.logger.info(f"🖱️ Clic sur le bouton: '{save_button.text}'")
            save_button.click()

            # Attendre la confirmation ou le retour à la liste
            try:
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'succès')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'créé')]")),
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.show")),
                        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Inventaire')]"))  # Retour à la liste
                    )
                )
                self.logger.info("✅ Sauvegarde confirmée")
                return True
            except Exception:
                self.logger.info("✅ Sauvegarde effectuée (confirmation non détectée)")
                time.sleep(3)
                return True

        except Exception as e:
            self.logger.error("❌ Erreur lors de la sauvegarde: %s", str(e))
            self.take_screenshot("save_error")
            return False

    def validate_newest_inventory(self):
        """Valider le nouvel inventaire créé"""
        try:
            self.logger.info("Recherche et validation du nouvel inventaire...")

            # Chercher tous les inventaires sur la page
            inventories = self.find_existing_inventories()

            # Chercher l'inventaire avec la date cible
            target_inventory = None
            for inventory in inventories:
                if inventory['date_str'] == self.target_date_str:
                    target_inventory = inventory
                    self.logger.info("Inventaire trouvé avec la date %s", self.target_date_str)
                    break

            if not target_inventory:
                self.logger.warning("Inventaire avec la date %s non trouvé", self.target_date_str)
                return False

            # Chercher le bouton de validation/activation pour cet inventaire
            row = target_inventory['row_element']

            # Boutons potentiels de validation
            validation_buttons = []

            # Chercher dans la ligne de l'inventaire
            try:
                # Chercher des boutons d'action dans la ligne
                buttons = row.find_elements(By.CSS_SELECTOR, "button, a.btn, .btn")
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.lower()
                        button_title = button.get_attribute('title') or ""
                        button_title = button_title.lower()

                        # Mots-clés pour les boutons de validation
                        validation_keywords = ['valider', 'activer', 'confirmer', 'lancer', 'démarrer', 'start']

                        if any(keyword in button_text or keyword in button_title for keyword in validation_keywords):
                            validation_buttons.append(button)
                            self.logger.info(f"Bouton de validation trouvé: '{button.text}' - '{button_title}'")

            except Exception as e:
                self.logger.warning("Erreur lors de la recherche de boutons dans la ligne: %s", str(e))

            # Si pas de bouton de validation spécifique trouvé, essayer de cliquer sur l'inventaire
            if not validation_buttons:
                self.logger.info("Aucun bouton de validation spécifique trouvé, tentative d'ouverture de l'inventaire")

                # Double-clic sur la ligne pour ouvrir l'inventaire
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.double_click(row).perform()

                    # Attendre l'ouverture
                    import time
                    time.sleep(3)

                    # Chercher des boutons de validation dans la page/modal ouverte
                    validation_buttons_in_modal = self._find_validation_buttons_in_current_page()
                    if validation_buttons_in_modal:
                        validation_buttons.extend(validation_buttons_in_modal)

                except Exception as e:
                    self.logger.warning("Erreur lors du double-clic sur l'inventaire: %s", str(e))

            # Essayer de cliquer sur les boutons de validation trouvés
            for button in validation_buttons:
                try:
                    self.logger.info(f"Clic sur le bouton de validation: '{button.text}'")
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    button.click()

                    # Attendre la confirmation
                    time.sleep(3)

                    # Vérifier si la validation a réussi (recherche de messages de succès ou changement d'état)
                    success_indicators = [
                        "//div[contains(@class, 'alert-success')]",
                        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'validé')]",
                        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'activé')]",
                        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirmé')]"
                    ]

                    validation_confirmed = False
                    for indicator in success_indicators:
                        try:
                            self.driver.find_element(By.XPATH, indicator)
                            validation_confirmed = True
                            self.logger.info("Confirmation de validation détectée")
                            break
                        except:
                            continue

                    if validation_confirmed:
                        return True
                    else:
                        self.logger.info("Bouton cliqué mais pas de confirmation explicite")
                        return True  # On considère que ça a marché

                except Exception as e:
                    self.logger.warning(f"Erreur lors du clic sur le bouton de validation: {e}")
                    continue

            self.logger.warning("Aucun bouton de validation n'a pu être activé")
            return False

        except Exception as e:
            self.logger.error("Erreur lors de la validation de l'inventaire: %s", str(e))
            return False

    def _find_validation_buttons_in_current_page(self):
        """Chercher des boutons de validation dans la page actuelle"""
        validation_buttons = []

        try:
            # Sélecteurs pour boutons de validation
            validation_selectors = [
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'valider')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'activer')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'lancer')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'démarrer')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirmer')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'valider')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'activer')]"
            ]

            for selector in validation_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            validation_buttons.append(button)
                            self.logger.info(f"Bouton de validation trouvé dans la page: '{button.text}'")
                except:
                    continue

        except Exception as e:
            self.logger.warning(f"Erreur lors de la recherche de boutons de validation: {e}")

        return validation_buttons

    def find_and_activate_draft_inventory(self):
        """Chercher et activer un inventaire brouillon"""
        try:
            # Prendre une capture d'écran pour voir l'état actuel
            self.take_screenshot("search_draft_inventory")

            # Chercher le bouton "Reprendre un inventaire archivé" visible dans les captures
            archive_button_selectors = [
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reprendre')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reprendre')]",
                ".btn[title*='reprendre']",
                ".btn-success"  # Le bouton vert "Reprendre un inventaire archivé"
            ]

            for selector in archive_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH if selector.startswith("//") else By.CSS_SELECTOR, selector)
                    for button in buttons:
                        button_text = button.text.lower()
                        if 'reprendre' in button_text and 'inventaire' in button_text:
                            self.logger.info(f"Bouton 'Reprendre' trouvé: {button.text}")
                            button.click()

                            import time
                            time.sleep(3)

                            # Chercher l'inventaire avec notre date dans la liste des archivés
                            archived_inventories = self.find_existing_inventories()
                            for inventory in archived_inventories:
                                if inventory['date_str'] == self.target_date_str:
                                    self.logger.info(f"Inventaire archivé trouvé: {inventory['date_str']}")

                                    # Essayer de l'activer
                                    if 'action_button' in inventory and inventory['action_button']:
                                        inventory['action_button'].click()
                                        time.sleep(2)
                                        return True
                                    elif 'row_element' in inventory:
                                        # Double-clic sur la ligne
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        actions = ActionChains(self.driver)
                                        actions.double_click(inventory['row_element']).perform()
                                        time.sleep(2)
                                        return True

                            # Revenir à la page principale
                            self.navigate_to_inventaires()
                            break
                except:
                    continue

            return False

        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'inventaire brouillon: {e}")
            return False

    def update_inventory_date(self, inventory_info):
        """Mettre à jour la date d'un inventaire spécifique"""
        try:
            self.logger.info("Mise à jour de l'inventaire du %s vers %s",
                           inventory_info['date_str'], self.target_date_str)

            # Attendre que tout modal/spinner disparaisse
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.ID, "modalSpinner"))
                )
            except:
                pass

            # Attendre qu'il n'y ait plus de modals ouverts
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
                )
            except:
                pass

            # Attendre un petit moment pour s'assurer que la page est stable
            import time
            time.sleep(2)

            # Méthode principale: Double-clic sur la ligne de l'inventaire
            if 'row_element' in inventory_info:
                row = inventory_info['row_element']
                self.logger.info("Double-clic sur la ligne de l'inventaire")

                # Scroll vers l'élément pour le rendre visible
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                time.sleep(1)

                # Double-clic sur la ligne
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.double_click(row).perform()

                # Attendre l'ouverture de la modal d'édition
                try:
                    self.wait.until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-body")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='date']")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='date']")),
                            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'date')]"))
                        )
                    )
                    self.logger.info("Modal d'édition ouverte")
                except:
                    self.logger.warning("Modal d'édition non détectée, tentative alternative")

            # Méthode alternative: Clic sur un bouton d'édition si présent
            elif 'action_button' in inventory_info and inventory_info['action_button']:
                action_button = inventory_info['action_button']
                self.driver.execute_script("arguments[0].scrollIntoView();", action_button)

                # Attendre que l'élément soit cliquable
                self.wait.until(EC.element_to_be_clickable(action_button))
                action_button.click()

                # Attendre l'ouverture de la modal/page d'édition
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='date']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='date']")),
                        EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'date')]")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-body"))
                    )
                )

            # Attendre un moment pour que la modal se charge complètement
            time.sleep(3)

            # Rechercher le champ de date à modifier avec des sélecteurs plus larges
            date_field = None
            date_selectors = [
                "input[type='date']",
                "input[placeholder*='date']",
                "input[name*='date']",
                "input[id*='date']",
                "input[class*='date']",
                "input[type='text']"  # Essayer tous les champs texte
            ]

            self.logger.info("Recherche du champ de date...")
            for selector in date_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for field in fields:
                        # Vérifier si le champ contient une date ou est vide et éditable
                        field_value = field.get_attribute('value') or ""
                        if ('/' in field_value and len(field_value) == 10) or field_value == "" or "date" in field.get_attribute('name', '').lower():
                            date_field = field
                            self.logger.info(f"Champ de date trouvé: {selector}, valeur actuelle: '{field_value}'")
                            break
                    if date_field:
                        break
                except NoSuchElementException:
                    continue

            if not date_field:
                self.logger.warning("Champ de date spécifique non trouvé, tentative avec tous les inputs")
                # En dernier recours, essayer tous les inputs visibles
                all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
                for input_field in all_inputs:
                    if input_field.is_displayed() and input_field.is_enabled():
                        date_field = input_field
                        self.logger.info(f"Utilisation du champ: {input_field.get_attribute('type')} - {input_field.get_attribute('name')}")
                        break

            if not date_field:
                self.logger.error("Impossible de trouver le champ de date à modifier")
                return False

            # Modifier la date
            self.logger.info(f"Modification de la date vers: {self.target_date_str}")

            # Vider le champ
            date_field.clear()
            time.sleep(0.5)

            # Saisir la nouvelle date
            if date_field.get_attribute('type') == 'date':
                # Format ISO pour input[type='date']
                iso_date = self.target_date.strftime('%Y-%m-%d')
                date_field.send_keys(iso_date)
                self.logger.info(f"Date saisie au format ISO: {iso_date}")
            else:
                # Format DD/MM/YYYY pour les champs texte
                date_field.send_keys(self.target_date_str)
                self.logger.info(f"Date saisie au format FR: {self.target_date_str}")

            time.sleep(1)

            # Sauvegarder les modifications
            self.logger.info("Tentative de sauvegarde...")
            save_success = self._save_changes()

            if save_success:
                self.logger.info("Date d'inventaire mise à jour avec succès")
                time.sleep(2)  # Attendre que la sauvegarde soit effective
                return True
            else:
                self.logger.error("Échec de la sauvegarde des modifications")
                return False

        except Exception as e:
            self.logger.error("Erreur lors de la mise à jour de la date: %s", str(e))
            self.take_screenshot("update_date_error")
            return False

    def _save_changes(self):
        """Sauvegarder les modifications"""
        try:
            import time
            # Essayer différentes méthodes de sauvegarde

            # Méthode 1: Bouton Sauvegarder/Enregistrer avec sélecteurs plus larges
            save_buttons = [
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sauvegarder')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enregistrer')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'valider')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirmer')]",
                "//button[contains(text(), 'OK')]",
                "//input[@type='submit']",
                "//button[@type='submit']",
                "//button[contains(@class, 'btn-primary')]",
                "//button[contains(@class, 'btn-success')]"
            ]

            self.logger.info("Recherche du bouton de sauvegarde...")
            for selector in save_buttons:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.logger.info(f"Bouton trouvé: {button.text} - {selector}")
                            button.click()
                            self.logger.info("Bouton de sauvegarde cliqué")

                            # Attendre la confirmation ou fermeture de modal
                            try:
                                self.wait.until(
                                    EC.any_of(
                                        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'succès')]")),
                                        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modifié')]")),
                                        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enregistré')]")),
                                        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))  # Modal fermée
                                    )
                                )
                                self.logger.info("Confirmation de sauvegarde détectée")
                                return True
                            except TimeoutException:
                                self.logger.info("Pas de confirmation explicite, mais bouton cliqué")
                                time.sleep(2)
                                return True
                except (NoSuchElementException, Exception) as e:
                    continue

            # Méthode 2: Appuyer sur Entrée sur le champ actif
            self.logger.info("Tentative de sauvegarde avec Entrée...")
            try:
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(Keys.RETURN)
                self.logger.info("Touche Entrée pressée pour sauvegarder")
                time.sleep(2)
                return True
            except:
                pass

            # Méthode 3: Cliquer à côté pour confirmer la saisie
            self.logger.info("Tentative de clic à côté pour confirmer...")
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.click()
                time.sleep(1)
                return True
            except:
                pass

            self.logger.warning("Aucune méthode de sauvegarde n'a fonctionné")
            return False

        except Exception as e:
            self.logger.error("Erreur lors de la sauvegarde: %s", str(e))
            return False

    def refresh_inventories(self):
        """Actualiser la page des inventaires"""
        try:
            self.logger.info("Actualisation de la page des inventaires")
            self.driver.refresh()

            # Attendre le rechargement
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Inventaire')]")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'inventaire')]"))
                )
            )

            self.take_screenshot("page_refreshed")
            self.logger.info("Page actualisée avec succès")
            return True

        except Exception as e:
            self.logger.error("Erreur lors de l'actualisation: %s", str(e))
            return False

    def run(self, update_all=True, days_range=None):
        """
        Méthode principale d'exécution du script

        Args:
            update_all: Si True, met à jour tous les inventaires trouvés
            days_range: Si spécifié, met à jour seulement les inventaires dans cette plage de jours
        """
        try:
            self.logger.info("=== DÉBUT DE LA MISE À JOUR DES DATES D'INVENTAIRES ===")

            # Validation des variables d'environnement
            if not self.validate_environment():
                return 2

            # Initialisation du driver
            if not self.setup_driver():
                return 2

            # Étapes d'automatisation
            steps = [
                ("Connexion", self.login),
                ("Navigation vers Inventaires", self.navigate_to_inventaires)
            ]

            for step_name, step_func in steps:
                self.logger.info("Étape: %s", step_name)
                if not step_func():
                    self.logger.error("Échec à l'étape: %s", step_name)
                    return 2

            # Rechercher les inventaires existants pour servir de template
            inventories = self.find_existing_inventories()

            if not inventories:
                self.logger.warning("Aucun inventaire trouvé pour servir de template")
                self.logger.info("Création d'un inventaire simple avec la date %s", self.target_date_str)

                # Créer un inventaire sans template
                if self.create_new_inventory():
                    self.logger.info("=== SUCCÈS: 1 inventaire créé avec la date %s ===", self.target_date_str)
                    return 0
                else:
                    return 2

            # Utiliser le premier inventaire comme template
            template_inventory = inventories[0]
            self.logger.info("Utilisation de l'inventaire '%s' comme template",
                           template_inventory.get('date_str', 'N/A'))

            # Créer un nouvel inventaire basé sur le template
            self.logger.info("Création d'un nouvel inventaire avec la date %s", self.target_date_str)

            if self.create_new_inventory(template_inventory):
                self.logger.info("Nouvel inventaire créé avec succès")

                # Attendre plus longtemps pour que l'inventaire soit traité
                import time
                time.sleep(5)

                # Actualiser plusieurs fois pour voir le nouvel inventaire
                for i in range(3):
                    self.refresh_inventories()
                    time.sleep(3)

                    # Vérifier si l'inventaire apparaît
                    inventories = self.find_existing_inventories()
                    for inventory in inventories:
                        if inventory['date_str'] == self.target_date_str:
                            self.logger.info("Inventaire trouvé après actualisation %d", i+1)
                            break
                    else:
                        continue
                    break

                # L'inventaire a été créé avec succès
                updated_count = 1
                self.logger.info("Inventaire créé avec succès")

                # Retourner à la page Inventaires pour vérification finale
                self.navigate_to_inventaires()
                time.sleep(2)

                # Vérification finale - chercher l'inventaire créé
                final_inventories = self.find_existing_inventories()
                inventory_found = False
                for inventory in final_inventories:
                    if inventory['date_str'] == self.target_date_str:
                        inventory_found = True
                        self.logger.info("✅ Inventaire confirmé visible dans la liste: %s", self.target_date_str)
                        break

                if not inventory_found:
                    # Chercher dans les archives/brouillons
                    self.logger.info("Inventaire non visible dans la liste principale, recherche dans les brouillons...")
                    if self.find_and_activate_draft_inventory():
                        self.logger.info("✅ Inventaire trouvé et activé depuis les brouillons")
                    else:
                        self.logger.warning("⚠️  Inventaire créé mais non visible (peut être en attente de validation)")
            else:
                updated_count = 0
                self.logger.error("Échec de la création du nouvel inventaire")

            # Actualiser la page pour voir les changements
            self.refresh_inventories()

            if updated_count > 0:
                self.logger.info("=== SUCCÈS: %d inventaire créé avec la date %s ===",
                               updated_count, self.target_date_str)
                return 0
            else:
                self.logger.error("=== ÉCHEC: Aucun inventaire créé ===")
                return 1

        except Exception as e:
            self.logger.error("Erreur inattendue: %s", str(e))
            self.take_screenshot("unexpected_error")
            return 2

        finally:
            # Nettoyage
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.info("Driver fermé proprement")
                except Exception as e:
                    self.logger.error("Erreur lors de la fermeture du driver: %s", str(e))


def main():
    """Point d'entrée principal avec arguments en ligne de commande"""
    import argparse

    parser = argparse.ArgumentParser(description='Mise à jour des dates d\'inventaires Satelix')
    parser.add_argument('--date', '-d',
                       help='Date cible au format DD/MM/YYYY (défaut: aujourd\'hui)')
    parser.add_argument('--days', '-n', type=int,
                       help='Mettre à jour seulement les inventaires des N derniers jours')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Mettre à jour tous les inventaires trouvés (défaut)')
    parser.add_argument('--update-today', action='store_true',
                       help='Créer un inventaire avec la date d\'aujourd\'hui')

    args = parser.parse_args()

    # Déterminer la date cible
    target_date = None
    if args.date:
        try:
            target_date = args.date
        except ValueError:
            print(f"Erreur: Format de date invalide '{args.date}'. Utilisez DD/MM/YYYY")
            sys.exit(1)
    elif args.update_today:
        # Pour --update-today, utiliser la date d'aujourd'hui
        from datetime import datetime
        target_date = datetime.now().strftime("%d/%m/%Y")

    # Initialiser et exécuter
    automation = SatelixInventoryDateUpdater(target_date)
    exit_code = automation.run(update_all=args.all or not args.days, days_range=args.days)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()