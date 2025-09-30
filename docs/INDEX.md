# 📚 Documentation - Serre Connectée

Bienvenue dans la documentation du projet **Serre Connectée** !

## 📖 Guides disponibles

### 🚀 Démarrage rapide
- **[QUICK_START.md](QUICK_START.md)** - Guide de démarrage en 5 minutes
  - Tests manuels (mock et matériel réel)
  - Installation du service systemd
  - Vérification des données
  - Commandes utiles

### 📦 Installation complète
- **[INSTALLATION.md](INSTALLATION.md)** - Guide d'installation détaillé
  - Prérequis système
  - Installation des dépendances
  - Configuration du service systemd
  - Dépannage complet
  - Scripts de monitoring

### 📊 État du projet
- **[STATUS.md](STATUS.md)** - État actuel du projet
  - Composants installés et testés
  - Fonctionnalités opérationnelles
  - Problèmes résolus
  - Métriques et statistiques
  - Prochaines étapes

### 🔧 Résolution de problèmes
- **[HARDWARE_FIXED.md](HARDWARE_FIXED.md)** - Résolution du problème SCD30
  - Diagnostic de l'erreur I/O (errno 121)
  - Solution appliquée
  - Tests de validation
  - Bonnes pratiques

### 🏗️ Refactorisation (Futur)
- **[REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)** - Plan de refactorisation SOLID
  - Analyse de l'architecture actuelle
  - Principes SOLID et Design Patterns
  - Nouveau schéma de base de données
  - API REST complète pour mobile
  - Roadmap d'implémentation sur 3 semaines

## 🗂️ Organisation de la documentation

```
docs/
├── README.md                    # Ce fichier - Index de la documentation
├── QUICK_START.md              # Démarrage rapide
├── INSTALLATION.md             # Installation complète
├── STATUS.md                   # État actuel du projet
├── HARDWARE_FIXED.md           # Résolution problème matériel
└── REFACTORING_GUIDE.md        # Plan de refactorisation
```

## 🎯 Par où commencer ?

### Si vous découvrez le projet
1. Lisez le [README principal](../README.md) à la racine du projet
2. Suivez le guide [QUICK_START.md](QUICK_START.md)
3. Consultez [STATUS.md](STATUS.md) pour voir l'état actuel

### Si vous installez le système
1. Suivez [INSTALLATION.md](INSTALLATION.md) étape par étape
2. En cas de problème avec le capteur, consultez [HARDWARE_FIXED.md](HARDWARE_FIXED.md)
3. Utilisez [QUICK_START.md](QUICK_START.md) pour tester

### Si vous voulez améliorer le code
1. Lisez [STATUS.md](STATUS.md) pour comprendre l'état actuel
2. Consultez [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) pour le plan d'amélioration
3. Suivez les principes SOLID décrits dans le guide

## 🔗 Liens utiles

### Fichiers importants du projet
- [README.md](../README.md) - Vue d'ensemble du projet
- [main.py](../main.py) - Point d'entrée de l'application
- [serre.service](../serre.service) - Fichier service systemd
- [requirements.txt](../requirements.txt) - Dépendances Python

### Scripts utiles
- [start_web.sh](../start_web.sh) - Démarrer l'interface web
- [stop_all.sh](../stop_all.sh) - Arrêter tous les processus
- [hardware_test_menu.py](../hardware_test_menu.py) - Menu de test matériel

### Tests
- [tests/test_hardware.py](../tests/test_hardware.py) - Tests automatiques du matériel

## 📝 Convention de documentation

Tous les documents suivent ces conventions :
- **Émojis** pour améliorer la lisibilité
- **Code blocks** avec syntaxe highlighting
- **Liens internes** pour naviguer facilement
- **Exemples concrets** pour chaque commande
- **Sections dépannage** pour les problèmes courants

## 🆘 Besoin d'aide ?

Si vous rencontrez un problème :
1. Consultez la section **Dépannage** dans [INSTALLATION.md](INSTALLATION.md)
2. Vérifiez [HARDWARE_FIXED.md](HARDWARE_FIXED.md) pour les problèmes matériels
3. Consultez [STATUS.md](STATUS.md) pour l'état actuel du système

---

*Documentation mise à jour le 30 septembre 2025*
