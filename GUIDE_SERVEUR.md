# 🖥️ GUIDE D'INSTALLATION SERVEUR

## 📋 Vue d'ensemble

Ce guide explique comment installer Satelix Automation Suite sur un serveur pour une exécution automatique quotidienne à 8h00.

## 🎯 Options d'installation

### 🔷 Option 1: Serveur Windows

#### Prérequis
- Windows Server 2016+ ou Windows 10+
- Python 3.8+ installé
- Droits administrateur
- Accès réseau à Satelix (sql-industrie:7980)

#### Installation
1. **Copier le dossier portable sur le serveur**
   ```
   C:\Automation\Satelix_Portable\
   ```

2. **Configurer les identifiants**
   - Modifier `app\.env` avec les vrais identifiants
   - Tester la connexion avec l'option [7] Diagnostic

3. **Programmer l'exécution automatique**
   - Lancer `DEMARRER_SATELIX.bat` en tant qu'administrateur
   - Choisir option [4] Automatisation quotidienne
   - La tâche sera créée dans le Planificateur de tâches Windows

#### Vérification
```cmd
# Vérifier que la tâche est créée
schtasks /query /tn "Satelix_Portable_Daily"

# Tester manuellement
schtasks /run /tn "Satelix_Portable_Daily"
```

### 🔷 Option 2: Serveur Linux

#### Prérequis
- Ubuntu/CentOS/RHEL 18.04+
- Python 3.8+ et pip installés
- Chrome/Chromium installé
- Accès réseau à Satelix

#### Installation
1. **Copier et adapter le script**
   ```bash
   # Créer le répertoire
   sudo mkdir -p /opt/satelix-automation
   cd /opt/satelix-automation

   # Copier les fichiers Python
   cp satelix_simple.py .
   cp requirements_portable.txt .

   # Installer les dépendances
   pip3 install -r requirements_portable.txt
   ```

2. **Créer le script de lancement**
   ```bash
   # Créer /opt/satelix-automation/run_daily.sh
   #!/bin/bash
   cd /opt/satelix-automation
   python3 satelix_simple.py --update-today
   ```

3. **Programmer avec cron**
   ```bash
   # Éditer le crontab
   sudo crontab -e

   # Ajouter cette ligne pour 8h00 du lundi au vendredi
   0 8 * * 1-5 /opt/satelix-automation/run_daily.sh >> /var/log/satelix.log 2>&1
   ```

## ⚙️ Configuration avancée

### Variables d'environnement
```bash
# Pour Linux, créer /opt/satelix-automation/.env
SATELIX_URL_LOGIN=http://sql-industrie:7980/
SATELIX_URL_INVENTAIRES=http://sql-industrie:7980/inventaire
SATELIX_USER=Geoffroy
SATELIX_PASSWORD=Crispin2025*
HEADLESS=true
TIMEOUT=30
```

### Logs et monitoring
```bash
# Vérifier les logs (Linux)
tail -f /var/log/satelix.log

# Vérifier les logs (Windows)
# Consultez l'Observateur d'événements ou le dossier logs\
```

## 🔧 Dépannage serveur

### Problèmes courants

1. **Erreur de connexion réseau**
   - Vérifier la connectivité: `telnet sql-industrie 7980`
   - Configurer le proxy si nécessaire

2. **Chrome non trouvé (Linux)**
   ```bash
   # Installer Chrome sur Ubuntu
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
   sudo apt update
   sudo apt install google-chrome-stable
   ```

3. **Problèmes de droits (Linux)**
   ```bash
   # Donner les permissions
   chmod +x /opt/satelix-automation/run_daily.sh
   chown -R www-data:www-data /opt/satelix-automation
   ```

## 📊 Monitoring et alertes

### Script de vérification
```bash
#!/bin/bash
# check_satelix.sh - Vérifier si l'automation fonctionne

LOG_FILE="/var/log/satelix.log"
TODAY=$(date +%Y-%m-%d)

if grep -q "$TODAY.*SUCCÈS" "$LOG_FILE"; then
    echo "✅ Satelix automation SUCCESS for $TODAY"
    exit 0
else
    echo "❌ Satelix automation FAILED for $TODAY"
    exit 1
fi
```

### Notifications par email
```bash
# Ajouter au crontab pour recevoir un email en cas d'échec
5 8 * * 1-5 /opt/satelix-automation/check_satelix.sh || echo "Satelix automation failed" | mail -s "ALERT: Satelix" admin@company.com
```

## 🚀 Mise en production

### Checklist finale
- [ ] Test manuel réussi
- [ ] Configuration des identifiants
- [ ] Tâche planifiée créée
- [ ] Logs configurés
- [ ] Monitoring en place
- [ ] Documentation à jour

### Sauvegarde
```bash
# Sauvegarder la configuration
tar -czf satelix-backup-$(date +%Y%m%d).tar.gz /opt/satelix-automation
```

## 📞 Support

En cas de problème:
1. Consulter les logs
2. Tester manuellement le script
3. Vérifier la connectivité réseau
4. Contacter Arthur si nécessaire