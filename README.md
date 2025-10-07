# 🚀 SATELIX AUTOMATION SUITE v2.0

## 📋 Démarrage rapide

### 🚀 **Interface Moderne (Recommandée)**
1. **Double-cliquez** sur `DEMARRER_SATELIX_MODERNE.bat`
2. Navigation intuitive avec ↑↓ et Entrée
3. Interface colorée et interactive

### 📄 **Interface Classique**
1. **Double-cliquez** sur `DEMARRER_SATELIX.bat`
2. Première fois: Choisissez **[1] Configuration initiale**
3. Usage quotidien: Choisissez **[2] Créer inventaires**

## ⚡ Fonctionnalités

- ✅ **Interface simple** - Menu numéroté, aucun code à comprendre
- ✅ **Création automatique** d'inventaires Satelix (type: Inventaire filtres / DEPOT / CMUP)
- ✅ **Planification** - Exécution automatique à 8h00 chaque matin
- ✅ **Diagnostic intégré** - Résolution automatique des problèmes de connexion
- ✅ **Portable** - Fonctionne sur clé USB, aucune installation

## 🎯 Menu principal

```
[1] Configuration initiale           <- Première installation
[2] Créer inventaires (aujourd'hui)  <- Usage quotidien
[3] Créer inventaires (date)         <- Date spécifique
[4] Automatisation quotidienne       <- Planification serveur
[5] Consulter les logs              <- Diagnostic
[6] Nettoyage des fichiers          <- Maintenance
[7] Diagnostic système              <- Dépannage auto
[8] Réparation automatique          <- Corrections
[9] Mode debug                      <- Chrome visible
[0] Quitter
```

## 🖥️ Installation serveur

### Windows Server
- Droits administrateur requis
- Option [4] configure automatiquement le Planificateur de tâches

### Linux Server
- Script `install_server_linux.sh` inclus
- Configuration cron automatique à 8h00

**Voir `GUIDE_SERVEUR.md` pour les détails complets**

## 📋 Prérequis

- Python 3.8+ installé
- Chrome/Chromium installé
- Réseau entreprise (accès à sql-industrie:7980)

## 🔒 Sécurité

- Identifiants stockés localement dans `.env`
- Chiffrement des communications
- Logs de traçabilité complets

## 📞 Support

**En cas de problème:**
1. Option [7] Diagnostic automatique
2. Option [8] Réparations automatiques
3. Consulter les logs dans `logs/`
4. Contacter Arthur si nécessaire

---
**🎯 Objectif: Automatisation Satelix sans connaissance technique requise**