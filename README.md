# 🍄 Serre Connectée - Projet IoT Raspberry Pi

Système de contrôle automatisé pour serre à champignons, propulsé par Raspberry Pi.

---

## 🎯 Vision du Projet

Ce projet explore l'**Internet des Objets (IoT)** appliqué à l'agriculture, en combinant autosuffisance alimentaire et innovation technologique. Conçu comme un système de gestion intelligent pour une serre à champignons, il offre un contrôle automatisé de l'environnement (température, humidité, CO2) via des capteurs et actionneurs connectés.

Au-delà du contrôle de serre, ce projet sert de **plateforme d'expérimentation** pour développer des compétences variées :
- Applications frontend (Electron desktop, Flutter mobile)
- Intelligence artificielle (analyse vidéo, assistant vocal)
- Optimisation par analyse de données
- Architecture logicielle moderne (SOLID, microservices)

---

## ✨ Fonctionnalités

### Contrôle Automatisé

- 📊 **Monitoring en temps réel** : Température, humidité, CO2 (capteur SCD30)
- 💡 **Éclairage intelligent** : LEDs programmables par plage horaire
- 💧 **Gestion de l'humidité** : Humidificateur à seuils configurables
- 🌬️ **Ventilation adaptative** : Extraction automatique selon niveau CO2

### Modes de Contrôle

- 🤖 **Mode automatique** : Gestion autonome selon paramètres configurés
- 🎮 **Mode manuel** : Contrôle direct via menu CLI ou API
- 🔌 **Simulation** : Mode mock pour développement sans matériel

### API REST Complète

- 🌐 **FastAPI** : API moderne avec documentation Swagger intégrée
- 🔐 **Authentification** : Sécurisé par token (X-API-Key)
- 📱 **Multi-plateforme** : Compatible Electron, Flutter, React, Vue, etc.
- 📈 **Historique** : Export des données pour analyse

---

## 🏗️ Architecture

```
Backend (Raspberry Pi)
├── Capteurs → SensorService → Orchestrateur → ActuatorCoordinator → Actionneurs
├── Configuration → ConfigurationManager → user_settings.json
├── Données → DataPersistence → SQLite
└── API REST → FastAPI (monitoring + contrôle)
```

**Principe SOLID** : Architecture modulaire avec services spécialisés, facilitant la maintenance et l'évolution.

---

## 🚀 Quick Start

### Installation

```bash
# Cloner le projet
git clone https://github.com/Ulysse-Dev-Serre/Projet_IoT_RaspberryPi.git
cd Projet_IoT_RaspberryPi

# Environnement virtuel
python3 -m venv myenv
source myenv/bin/activate

# Dépendances
pip install -r requirements.txt
```

### Lancement

```bash
# Mode simulation (sans matériel)
export HARDWARE_ENV=mock
python main.py

# Mode réel (avec matériel connecté)
export HARDWARE_ENV=raspberry_pi
export API_KEY="votre-cle-secrete"
python main.py
```

L'API sera accessible sur : `http://<IP_RASPBERRY>:5000/docs`

📖 **Guide complet** : [docs/1-fundation/SETUP.md](docs/1-fundation/SETUP.md)

---

## 📚 Documentation

### Pour Démarrer

- **[docs/1-fundation/SETUP.md](docs/1-fundation/SETUP.md)** - Installation pas à pas
- **[docs/1-fundation/ARCHITECTURE.md](docs/1-fundation/ARCHITECTURE.md)** - Structure du code
- **[docs/1-fundation/HARDWARE.md](docs/1-fundation/HARDWARE.md)** - Configuration matérielle

### Pour Développer

- **[docs/FRONTEND_CONNECT.md](docs/FRONTEND_CONNECT.md)** - ⭐ Connecter une app frontend
- **[docs/2-logic/CORE_LOGIC.md](docs/2-logic/CORE_LOGIC.md)** - Logique métier
- **[docs/3-api/API_GUIDE.md](docs/3-api/API_GUIDE.md)** - API REST

### Pour Référence

- **[docs/1-fundation/COMMANDES_UTILES.md](docs/1-fundation/COMMANDES_UTILES.md)** - Toutes les commandes
- **[docs/INDEX.md](docs/INDEX.md)** - Navigation complète

---

## 🧪 Tests

```bash
# Tests API (9 tests automatiques)
python scripts/test_api_simple.py

# Tests unitaires
pytest

# Test matériel
python scripts/hardware_test_menu.py
```

---

## 🛠️ Stack Technique

**Backend** :
- Python 3.9+
- FastAPI (API REST)
- SQLite (base de données)
- lgpio (contrôle GPIO)

**Matériel** :
- Raspberry Pi 5
- Capteur SCD30 (I2C)
- Relais 4 canaux
- LEDs, ventilateur, humidificateur ultrasonique

**Architecture** :
- SOLID principles
- Observer pattern (capteurs → orchestrateur)
- Dependency injection (orchestrateur → API)
- Thread-safe (verrous pour contrôle concurrent)

---

## 🚀 Évolutions Futures

- [ ] WebSocket pour temps réel (remplacer polling)
- [ ] Interface web React/Vue
- [ ] Application mobile Flutter
- [ ] Application desktop Electron
- [ ] IA analyse vidéo (détection croissance champignons)
- [ ] Assistant vocal (statut, contrôle)
- [ ] Machine learning (optimisation environnement)
- [ ] Dashboard analytics avec graphiques
- [ ] Export CSV/PDF des données
- [ ] Notifications push (alertes)

---

## 🤝 Contribuer

Les contributions sont bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout fonctionnalité X'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE.md).

---

## 👤 Auteur

Développé par **Ulysse** dans le cadre d'études en développement de systèmes.

Projet combinant passion pour l'autosuffisance alimentaire et innovation technologique.

---

## 🔗 Liens Utiles

- **Documentation complète** : [docs/INDEX.md](docs/INDEX.md)
- **Guide frontend** : [docs/FRONTEND_CONNECT.md](docs/FRONTEND_CONNECT.md)
- **API Swagger** : `http://<IP_RASPBERRY>:5000/docs`
- **Repository** : [GitHub](https://github.com/Ulysse-Dev-Serre/Projet_IoT_RaspberryPi)

---

⭐ **Star ce projet** si vous le trouvez utile !
