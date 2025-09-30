# Setup - Installation Depuis Zéro

Ce guide vous accompagne pour installer et tester le projet sur un Raspberry Pi après avoir cloné le dépôt.

## Étape 1 : Prérequis

- Raspberry Pi (testé sur Raspberry Pi 5)
- Raspberry Pi OS installé
- Python 3.9+
- Git

## Étape 2 : Cloner le Projet

```bash
cd ~
git clone https://github.com/Ulysse-Dev-Serre/Projet_IoT_RaspberryPi.git
cd Projet_IoT_RaspberryPi
```

## Étape 3 : Créer l'Environnement Virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv myenv

# Activer l'environnement
source myenv/bin/activate
```

Votre terminal devrait maintenant afficher `(myenv)` au début de la ligne.

## Étape 4 : Installer les Dépendances

```bash
pip install -r requirements.txt
```

## Étape 5 : Premier Test Rapide

```bash
python main.py
```

**Résultat attendu** :
- L'application démarre
- Un menu interactif s'affiche
- Vous pouvez naviguer avec les chiffres (1-9, 0, q)

Appuyez sur `Ctrl+C` pour arrêter.

---

## Test 2 : Mode Mock (Simulation)

Pour tester sans matériel connecté :

```bash
# Configurer le mode simulation
export HARDWARE_ENV=mock
export DB_TYPE=sqlite

# Lancer
python main.py
```

**Ce que vous verrez** :
```
Mode Matériel (HARDWARE_ENV): mock
Utilisation de MockHardware
MOCK: LEDs activées.
```

Les actionneurs sont simulés, aucun GPIO réel n'est utilisé. Parfait pour développer sans câblage.

---

## Test 3 : Mode Réel (Matériel Connecté)

**⚠️ Vérifiez que vos capteurs et actionneurs sont bien connectés avant de lancer !**

```bash
# Configurer le mode matériel réel
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite

# Lancer
python main.py
```

**Ce que vous verrez** :
```
Mode Matériel (HARDWARE_ENV): raspberry_pi
Utilisation de RaspberryPiHardware
GPIO chip (lgpio) ouvert.
Capteur SCD30 prêt! Température initiale: 25.6°C
LEDs activé(e) (GPIO 27 mis à 0)
```

### Test manuel des actionneurs

Dans le menu :
- Appuyez sur `1` pour activer les LEDs → Les LEDs réelles s'allument
- Appuyez sur `2` pour désactiver les LEDs → Les LEDs s'éteignent
- Appuyez sur `7` pour repasser en mode AUTO

📖 **Configuration matérielle** : [HARDWARE.md](HARDWARE.md)

---

## Configuration de l'API (Optionnel)

Pour activer l'API FastAPI avec contrôle à distance :

```bash
export API_KEY="votre-cle-secrete-ici"
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite

python main.py
```

L'API sera accessible sur : `http://<IP_RASPBERRY>:5000/docs`

📖 **Documentation complète** : [docs/API_ELECTRON.md](../API_ELECTRON.md)

---

## Base de Données

Par défaut, le projet utilise **SQLite** (fichier local `data/serre.db`).

Pour utiliser **PostgreSQL** :
1. Installer PostgreSQL
2. Créer la base de données
3. Configurer les variables d'environnement

📖 **Documentation base de données** : Voir [COMMANDES_UTILES.md](COMMANDES_UTILES.md#base-de-données)

---

## Démarrage Automatique (Service Systemd)

Pour que la serre démarre automatiquement au boot du Raspberry Pi :

### 1. Copier le fichier service

```bash
sudo cp serre.service /etc/systemd/system/
```

### 2. Recharger systemd

```bash
sudo systemctl daemon-reload
```

### 3. Activer au démarrage

```bash
sudo systemctl enable serre.service
```

### 4. Démarrer le service

```bash
sudo systemctl start serre.service
```

### 5. Vérifier l'état

```bash
sudo systemctl status serre.service
```

### 6. Voir les logs en temps réel

```bash
sudo journalctl -u serre.service -f
```

**Le service démarre automatiquement** :
- Au boot du Raspberry Pi
- Après un crash (redémarrage automatique)
- Avec les bonnes variables d'environnement (configurées dans `serre.service`)

---

## Résumé des Commandes Utiles

```bash
# Activer l'environnement
source myenv/bin/activate

# Lancer en mode mock
export HARDWARE_ENV=mock && python main.py

# Lancer en mode réel
export HARDWARE_ENV=raspberry_pi && python main.py

# Lancer avec l'API
export API_KEY="test-key" && python main.py

# Arrêter tous les processus Python
bash scripts/stop_all.sh

# Voir les logs du service
sudo journalctl -u serre.service -f
```

📖 **Toutes les commandes** : [COMMANDES_UTILES.md](COMMANDES_UTILES.md)

---

## Prochaines Étapes

1. ✅ Installation terminée
2. ✅ Test du matériel réussi
3. 📚 Lire l'[ARCHITECTURE.md](ARCHITECTURE.md) pour comprendre le code
4. 🔧 Configurer `data/user_settings.json` pour personnaliser les seuils
5. 🌐 Développer une app Electron avec [API_ELECTRON.md](../API_ELECTRON.md)
