#!/bin/bash
# Script d'installation automatique pour serveur Linux
# Satelix Automation Suite - Installation serveur

set -e  # Arrêter en cas d'erreur

echo "======================================================"
echo "    INSTALLATION SATELIX AUTOMATION - SERVEUR LINUX"
echo "======================================================"
echo

# Variables
INSTALL_DIR="/opt/satelix-automation"
SERVICE_USER="satelix"
LOG_DIR="/var/log/satelix"

# Vérifier les droits root
if [[ $EUID -ne 0 ]]; then
   echo "[X] Ce script doit être exécuté en tant que root"
   echo "    Utilisez: sudo $0"
   exit 1
fi

echo "[*] Création de l'utilisateur de service..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
    echo "[OK] Utilisateur $SERVICE_USER créé"
else
    echo "[i] Utilisateur $SERVICE_USER existe déjà"
fi

echo "[*] Création des répertoires..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"

echo "[*] Installation des dépendances système..."
if command -v apt-get >/dev/null; then
    # Ubuntu/Debian
    apt-get update
    apt-get install -y python3 python3-pip wget gnupg

    # Installation Chrome
    if ! command -v google-chrome >/dev/null; then
        echo "[*] Installation de Google Chrome..."
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
        apt-get update
        apt-get install -y google-chrome-stable
    fi

elif command -v yum >/dev/null; then
    # CentOS/RHEL
    yum install -y python3 python3-pip wget

    # Installation Chrome
    if ! command -v google-chrome >/dev/null; then
        echo "[*] Installation de Google Chrome..."
        cat > /etc/yum.repos.d/google-chrome.repo << 'EOF'
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/$basearch
enabled=1
gpgcheck=1
gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub
EOF
        yum install -y google-chrome-stable
    fi
else
    echo "[X] Gestionnaire de paquets non supporté"
    exit 1
fi

echo "[*] Copie des fichiers..."
# Ces fichiers doivent être copiés manuellement ou via SCP
if [ -f "./satelix_simple.py" ]; then
    cp ./satelix_simple.py "$INSTALL_DIR/"
    cp ./requirements_portable.txt "$INSTALL_DIR/"
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"/*
else
    echo "[!] Fichiers manquants. Copiez manuellement:"
    echo "    - satelix_simple.py"
    echo "    - requirements_portable.txt"
    echo "    vers $INSTALL_DIR/"
fi

echo "[*] Installation des dépendances Python..."
cd "$INSTALL_DIR"
pip3 install -r requirements_portable.txt

echo "[*] Création du script de lancement..."
cat > "$INSTALL_DIR/run_daily.sh" << 'EOF'
#!/bin/bash
cd /opt/satelix-automation
export DISPLAY=:99
python3 satelix_simple.py --update-today >> /var/log/satelix/automation.log 2>&1
EOF

chmod +x "$INSTALL_DIR/run_daily.sh"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/run_daily.sh"

echo "[*] Configuration du fichier .env..."
cat > "$INSTALL_DIR/.env" << 'EOF'
# Configuration Satelix - Serveur Linux
SATELIX_URL_LOGIN=http://sql-industrie:7980/
SATELIX_URL_INVENTAIRES=http://sql-industrie:7980/inventaire
SATELIX_USER=Geoffroy
SATELIX_PASSWORD=Crispin2025*

# Configuration serveur
HEADLESS=true
TIMEOUT=30
EOF

chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
chmod 600 "$INSTALL_DIR/.env"

echo "[*] Configuration du cron..."
# Créer la tâche cron pour l'utilisateur satelix
cat > /tmp/satelix_cron << 'EOF'
# Création automatique d'inventaires Satelix - Tous les jours ouvrables à 8h00
0 8 * * 1-5 /opt/satelix-automation/run_daily.sh
EOF

sudo -u "$SERVICE_USER" crontab /tmp/satelix_cron
rm /tmp/satelix_cron

echo "[*] Configuration de la rotation des logs..."
cat > /etc/logrotate.d/satelix << 'EOF'
/var/log/satelix/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 satelix satelix
}
EOF

echo "[*] Création du script de vérification..."
cat > "$INSTALL_DIR/check_health.sh" << 'EOF'
#!/bin/bash
# Script de vérification de santé

LOG_FILE="/var/log/satelix/automation.log"
TODAY=$(date +%Y-%m-%d)

if [ -f "$LOG_FILE" ] && grep -q "$TODAY.*SUCCÈS\|$TODAY.*SUCCESS" "$LOG_FILE"; then
    echo "[OK] Automation SUCCESS for $TODAY"
    exit 0
else
    echo "[X] Automation FAILED or not run for $TODAY"
    exit 1
fi
EOF

chmod +x "$INSTALL_DIR/check_health.sh"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/check_health.sh"

echo
echo "======================================================"
echo "          INSTALLATION TERMINÉE AVEC SUCCÈS"
echo "======================================================"
echo
echo "[OK] Satelix Automation installé dans: $INSTALL_DIR"
echo "[OK] Logs disponibles dans: $LOG_DIR"
echo "[OK] Tâche cron configurée: 8h00 du lundi au vendredi"
echo
echo "PROCHAINES ÉTAPES:"
echo "1. Tester la connexion:"
echo "   sudo -u $SERVICE_USER $INSTALL_DIR/run_daily.sh"
echo
echo "2. Vérifier les logs:"
echo "   tail -f $LOG_DIR/automation.log"
echo
echo "3. Vérifier le cron:"
echo "   sudo -u $SERVICE_USER crontab -l"
echo
echo "4. Tester la santé:"
echo "   $INSTALL_DIR/check_health.sh"
echo
echo "======================================================"