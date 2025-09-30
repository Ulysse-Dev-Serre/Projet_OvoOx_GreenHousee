# 📚 Documentation - Serre Connectée

Index de toute la documentation du projet.

---

## 🚀 Démarrage Rapide

**Nouveau sur le projet ?** Commencez ici :

1. **[1-fundation/SETUP.md](1-fundation/SETUP.md)** - Installation depuis zéro
   - Cloner → myenv → requirements → test
   - Mode mock vs mode réel
   - Configuration service systemd

2. **[1-fundation/COMMANDES_UTILES.md](1-fundation/COMMANDES_UTILES.md)** - Commandes quotidiennes
   - Lancement (mock/réel/API)
   - Service systemd
   - Base de données
   - Tests
   - Logs

---

## 📖 Documentation par Thème

### 1️⃣ Foundation (Bases)

| Fichier | Description |
|---------|-------------|
| **[ARCHITECTURE.md](1-fundation/ARCHITECTURE.md)** | Structure du projet (arbre de fichiers) |
| **[SETUP.md](1-fundation/SETUP.md)** | Installation et premiers tests |
| **[HARDWARE.md](1-fundation/HARDWARE.md)** | Configuration matérielle (GPIO, capteurs, câblage) |
| **[COMMANDES_UTILES.md](1-fundation/COMMANDES_UTILES.md)** | Toutes les commandes utiles |

### 2️⃣ Logic (Logique Métier)

| Fichier | Description |
|---------|-------------|
| **[CORE_LOGIC.md](2-logic/CORE_LOGIC.md)** | Fonctionnement de l'orchestrateur et services |

### 3️⃣ API

| Fichier | Description |
|---------|-------------|
| **[API_GUIDE.md](3-api/API_GUIDE.md)** | Documentation de l'API REST (curl, endpoints) |
| **[FRONTEND_CONNECT.md](FRONTEND_CONNECT.md)** | **⭐ Guide pour connecter un frontend (Electron, Flutter, etc.)** |

### 🗄️ Legacy (Archives)

| Fichier | Description |
|---------|-------------|
| **[legacy/README_LEGACY.md](legacy/README_LEGACY.md)** | Fichiers obsolètes archivés |
| **[legacy/index.html](legacy/index.html)** | Ancien template Flask (remplacé par FastAPI) |
| **[legacy/serre_logic.py](legacy/serre_logic.py)** | Ancien contrôleur monolithique (remplacé par Orchestrator) |

### 📝 Autres

| Fichier | Description |
|---------|-------------|
| **[REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)** | Architecture SOLID détaillée |

---

## 🎯 Guide par Scénario

### Scénario 1 : Je veux installer le projet

1. [SETUP.md](1-fundation/SETUP.md) - Étapes d'installation
2. [HARDWARE.md](1-fundation/HARDWARE.md) - Brancher le matériel
3. [COMMANDES_UTILES.md](1-fundation/COMMANDES_UTILES.md#service-systemd) - Configurer le service

### Scénario 2 : Je veux comprendre le code

1. [ARCHITECTURE.md](1-fundation/ARCHITECTURE.md) - Structure des fichiers
2. [CORE_LOGIC.md](2-logic/CORE_LOGIC.md) - Fonctionnement de la logique
3. [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) - Principes SOLID

### Scénario 3 : Je veux développer une app Electron/Flutter

1. **[FRONTEND_CONNECT.md](FRONTEND_CONNECT.md)** ⭐ - Tout ce dont vous avez besoin
2. [API_GUIDE.md](3-api/API_GUIDE.md) - Exemples curl
3. Swagger UI : `http://<IP>:5000/docs`

### Scénario 4 : J'ai un problème

1. [COMMANDES_UTILES.md](1-fundation/COMMANDES_UTILES.md) - Commandes de dépannage
2. [HARDWARE.md](1-fundation/HARDWARE.md#-dépannage-matériel) - Problèmes matériels
3. [CORE_LOGIC.md](2-logic/CORE_LOGIC.md#-dépannage) - Problèmes logiciels

### Scénario 5 : Je veux tester que tout fonctionne

```bash
# Tests API (9 tests automatiques)
python scripts/test_api_simple.py

# Tests unitaires
pytest

# Test matériel
python scripts/emergency_gpio_off.py  # Arrêt urgence
```

---

## 📂 Structure de la Documentation

```
docs/
├── INDEX.md                           # Ce fichier - Navigation
│
├── 1-fundation/                       # Documentation de base
│   ├── ARCHITECTURE.md                # Structure du projet
│   ├── SETUP.md                       # Installation complète
│   ├── HARDWARE.md                    # Configuration matérielle
│   └── COMMANDES_UTILES.md            # Commandes quotidiennes
│
├── 2-logic/                           # Logique métier
│   └── CORE_LOGIC.md                  # Orchestrateur et services
│
├── 3-api/                             # API REST
│   └── API_GUIDE.md                   # Guide API avec curl
│
├── legacy/                            # Archives
│   ├── README_LEGACY.md               # Explication fichiers obsolètes
│   ├── index.html                     # Ancien frontend Flask
│   └── serre_logic.py                 # Ancien contrôleur monolithique
│
├── FRONTEND_CONNECT.md                # ⭐ Guide frontend (Electron, Flutter)
└── REFACTORING_GUIDE.md               # Architecture SOLID détaillée
```

---

## 🔗 Liens Externes

- **Repository GitHub** : [Projet_IoT_RaspberryPi](https://github.com/Ulysse-Dev-Serre/Projet_IoT_RaspberryPi)
- **Swagger UI** : `http://<IP_RASPBERRY>:5000/docs`

---

## 📝 Dernières Mises à Jour

**Version 3.0.0** - 30 septembre 2025
- ✅ API complète avec contrôle (injection orchestrateur)
- ✅ Authentification par token (X-API-Key)
- ✅ Durées ON/OFF exposées (on_duration, off_duration)
- ✅ 7 paramètres de configuration
- ✅ Scripts de test automatiques
- ✅ Documentation restructurée et simplifiée
- ✅ FRONTEND_CONNECT.md créé (guide unique pour tous les frameworks)

---

*Dernière mise à jour : 30 septembre 2025*
