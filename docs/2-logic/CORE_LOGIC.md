# 🧠 Logique du Cœur Applicatif - Guide Simple

## Vue d'ensemble

Le système de la serre fonctionne comme une boucle :
1. **Lire les capteurs** (température, humidité, CO2)
2. **Décider quoi faire** (allumer/éteindre les appareils)
3. **Sauvegarder les données** (dans la base de données)
4. **Répéter** toutes les 15 secondes

## 🗂️ Organisation des fichiers

```
src/core/
├── orchestrator.py              ← Chef d'orchestre (coordonne tout)
│
├── services/                    ← Services spécialisés
│   ├── sensor_service.py        ← Lit les capteurs
│   ├── configuration_manager.py ← Gère les paramètres
│   ├── actuator_coordinator.py  ← Contrôle les appareils
│   └── data_persistence_service.py ← Sauvegarde en base
│
└── actuators/                   ← Logique de chaque appareil
    ├── led_controller.py        ← Logique des LEDs
    ├── humidifier_controller.py ← Logique de l'humidificateur
    └── ventilation_controller.py ← Logique de la ventilation
```

## 📖 Explication fichier par fichier

### 1. orchestrator.py - Le Chef d'Orchestre

**Rôle :** Coordonne tous les services, ne fait rien directement

**Ce qu'il fait :**
- Crée tous les services au démarrage
- Dit à `sensor_service` de lire les capteurs
- Quand il y a de nouvelles données :
  - Dit à `actuator_coordinator` de mettre à jour les appareils
  - Dit à `data_persistence` de sauvegarder

**Méthodes importantes :**
- `__init__()` - Initialise tout
- `_on_sensor_data(data)` - Appelée quand il y a nouvelles données capteurs
- `get_status()` - Donne l'état actuel (temp, humidité, CO2, appareils)
- `shutdown()` - Arrête tout proprement

**Fichier utilisé par :** `main.py`, `src/api/app.py`

---

### 2. sensor_service.py - Lecture des Capteurs

**Rôle :** Lire le capteur SCD30 en boucle

**Ce qu'il fait :**
- Toutes les 15 secondes : lit température, humidité, CO2
- Stocke la dernière valeur lue
- Notifie les observateurs (l'orchestrateur)

**Appareils concernés :**
- 📡 **Capteur SCD30** (I2C, adresse 0x61)
  - Lit via `hardware.lire_capteur()`

**Méthodes importantes :**
- `start()` - Démarre la lecture en boucle
- `get_latest_data()` - Retourne la dernière lecture
- `subscribe(callback)` - S'abonner aux nouvelles données
- `stop()` - Arrête la lecture

**Thread utilisé :** `SensorAcquisitionService` (daemon)

---

### 3. configuration_manager.py - Gestion des Paramètres

**Rôle :** Charger et sauvegarder les paramètres

**Ce qu'il fait :**
- Charge `data/user_settings.json` au démarrage
- Fournit les paramètres aux contrôleurs d'appareils
- Sauvegarde les modifications

**Paramètres gérés :**
- `HEURE_DEBUT_LEDS` : Quand allumer les LEDs (ex: 9h)
- `HEURE_FIN_LEDS` : Quand éteindre les LEDs (ex: 20h)
- `SEUIL_HUMIDITE_ON` : Humidité pour activer humidificateur (ex: 75%)
- `SEUIL_HUMIDITE_OFF` : Humidité pour désactiver humidificateur (ex: 85%)
- `SEUIL_CO2_MAX` : CO2 pour activer ventilation (ex: 1200 ppm)

**Méthodes importantes :**
- `get(key, default)` - Récupère un paramètre
- `get_all()` - Récupère tous les paramètres
- `update(changes)` - Modifie des paramètres
- `save_settings()` - Sauvegarde dans le fichier JSON

**Fichier utilisé :** `data/user_settings.json`

---

### 4. actuator_coordinator.py - Contrôle des Appareils

**Rôle :** Coordonner les 3 appareils (LEDs, humidificateur, ventilation)

**Ce qu'il fait :**
- Reçoit les données capteurs
- Dit à chaque contrôleur de se mettre à jour
- Gère le mode manuel/automatique

**Appareils concernés :**
- 💡 **LEDs** (GPIO 27)
- 💧 **Humidificateur** (GPIO 26 + 13)
  - Ventilateur (GPIO 26)
  - Brumisateur (GPIO 13)
- 🌬️ **Ventilation** (GPIO 22)

**Méthodes importantes :**
- `update_from_sensor_data(data)` - Met à jour tous les appareils
- `set_led_manual_mode(actif, état)` - Contrôle manuel LEDs
- `set_humidifier_manual_mode(actif, état)` - Contrôle manuel humidificateur
- `set_ventilation_manual_mode(actif, état)` - Contrôle manuel ventilation
- `set_all_auto_mode()` - Remet tout en automatique
- `emergency_stop_all()` - Éteint tout immédiatement

**Utilise :** `led_controller`, `humidifier_controller`, `ventilation_controller`

---

### 5. data_persistence_service.py - Sauvegarde

**Rôle :** Sauvegarder les données dans SQLite

**Ce qu'il fait :**
- Reçoit données capteurs + état des appareils
- Les ajoute dans un buffer
- Écrit dans SQLite quand :
  - 10 enregistrements dans le buffer OU
  - 5 minutes écoulées

**Base de données :**
- 📁 **SQLite** : `data/serre.db`
- 📊 **Table** : `sensor_data`

**Méthodes importantes :**
- `save_sensor_data(data, status)` - Ajoute au buffer
- `flush()` - Force l'écriture en BD
- `close()` - Ferme la BD proprement

**Fichier utilisé :** `data/serre.db`

---

### 6. Contrôleurs d'Appareils (actuators/)

Chaque appareil a son propre fichier avec sa logique.

#### led_controller.py - LEDs

**Logique :** Allumer entre `HEURE_DEBUT_LEDS` et `HEURE_FIN_LEDS`

```
Si heure actuelle entre 9h et 20h
  → Allumer LEDs
Sinon
  → Éteindre LEDs
```

**Appareil contrôlé :**
- 💡 LEDs (GPIO 27)
- État : `activer_leds()` ou `desactiver_leds()`

---

#### humidifier_controller.py - Humidificateur

**Logique :** Maintenir l'humidité entre deux seuils

```
Si humidité < 75%
  → Allumer humidificateur
Si humidité > 85%
  → Éteindre humidificateur
```

**Appareils contrôlés :**
- 💧 Ventilateur humidificateur (GPIO 26)
- 💧 Brumisateur (GPIO 13)
- État : `activer_humidificateur()` ou `desactiver_humidificateur()`

---

#### ventilation_controller.py - Ventilation

**Logique :** Évacuer le CO2 quand il est trop élevé

```
Si CO2 > 1200 ppm
  → Allumer ventilation
Sinon
  → Éteindre ventilation
```

**Appareil contrôlé :**
- 🌬️ Ventilateur (GPIO 22)
- État : `activer_ventilation()` ou `desactiver_ventilation()`

---

## 🔄 Flux de fonctionnement

### Démarrage
```
1. main.py démarre
2. Orchestrateur s'initialise
   ├─ Crée sensor_service
   ├─ Crée config_manager
   ├─ Crée les 3 contrôleurs (LED, humid, vent)
   ├─ Crée actuator_coordinator
   └─ Crée data_persistence
3. sensor_service démarre la lecture
4. Menu CLI s'affiche
```

### Boucle normale (toutes les 15s)
```
1. sensor_service lit les capteurs
   └─ Température, humidité, CO2
   
2. sensor_service notifie l'orchestrateur
   
3. Orchestrateur appelle actuator_coordinator
   ├─ led_controller vérifie l'heure → active/désactive
   ├─ humidifier_controller vérifie humidité → active/désactive
   └─ ventilation_controller vérifie CO2 → active/désactive
   
4. Orchestrateur appelle data_persistence
   └─ Sauvegarde tout dans SQLite
```

### Contrôle manuel (via menu CLI ou API)
```
1. Utilisateur appuie sur "1" (activer LEDs)
2. Menu appelle orchestrator.set_leds_manual_mode(True, True)
3. Orchestrateur appelle actuator_coordinator
4. Coordinator active le mode manuel sur led_controller
5. led_controller force l'état à ON
6. GPIO 27 est mis à 0 (ON)
7. Les LEDs s'allument 💡
```

## 🔌 Appareils et GPIO

| Appareil | Type | GPIO | État ON | État OFF |
|----------|------|------|---------|----------|
| LEDs | Relais | 27 | 0 | 1 |
| Ventilateur humid | Relais | 26 | 0 | 1 |
| Brumisateur | Relais | 13 | 0 | 1 |
| Ventilation | Relais | 22 | 0 | 1 |
| Capteur SCD30 | I2C | - | - | - |

**Note :** GPIO = 0 active le relais (logique inverse)

## 📊 Données sauvegardées

Chaque enregistrement dans SQLite contient :
```
- timestamp : Date et heure
- temperature : Température en °C
- humidity : Humidité en %
- co2 : CO2 en ppm
- leds_active : LEDs ON/OFF
- humidifier_active : Humidificateur ON/OFF
- ventilation_active : Ventilation ON/OFF
- *_duration_seconds : Durées ON/OFF de chaque appareil
```

## 🛠️ Modifier le comportement

### Changer les horaires des LEDs
**Fichier :** Modifier dans le menu CLI (option 9) ou éditer `data/user_settings.json`
```json
{
  "HEURE_DEBUT_LEDS": 8,
  "HEURE_FIN_LEDS": 22
}
```

### Changer les seuils d'humidité
**Fichier :** `data/user_settings.json`
```json
{
  "SEUIL_HUMIDITE_ON": 70.0,
  "SEUIL_HUMIDITE_OFF": 85.0
}
```

### Changer le seuil de CO2
**Fichier :** `data/user_settings.json`
```json
{
  "SEUIL_CO2_MAX": 1500.0
}
```

### Changer les GPIO
**Fichier :** `src/config.py` (nécessite redémarrage)
```python
PIN_LEDS = 27
VENTILATION_OUTPUT_PIN = 22
PIN_FAN_HUMIDIFICATEUR = 26
PIN_BRUMISATEUR = 13
```

## 🐛 Dépannage

### Un appareil ne s'allume pas

1. **Vérifier le mode :** Est-il en AUTO ou MANUEL ?
   - Menu CLI → option 0 pour rafraîchir l'affichage
   
2. **Vérifier les conditions :**
   - LEDs : Est-ce entre les heures configurées ?
   - Humidificateur : L'humidité est-elle < 75% ?
   - Ventilation : Le CO2 est-il > 1200 ppm ?

3. **Vérifier le GPIO :**
   - Logs : `tail -f data/logs/serre_controller.log`
   - Chercher : "GPIO X mis à 0" (activé) ou "GPIO X mis à 1" (désactivé)

### Les capteurs retournent None

1. **Vérifier I2C :**
   ```bash
   sudo i2cdetect -y 1
   # Le capteur doit apparaître à 0x61
   ```

2. **Vérifier les logs :**
   ```bash
   tail -f data/logs/serre_controller.log | grep SCD30
   ```

### La base de données ne s'écrit pas

1. **Vérifier les permissions :**
   ```bash
   ls -l data/serre.db
   ```

2. **Vérifier les logs :**
   ```bash
   tail -f data/logs/serre_controller.log | grep sqlite
   ```

## 📝 Résumé des responsabilités

| Service | Responsabilité | Interagit avec |
|---------|----------------|----------------|
| **SensorAcquisitionService** | Lire capteurs | Capteur SCD30 (I2C) |
| **ConfigurationManager** | Gérer paramètres | user_settings.json |
| **ActuatorCoordinator** | Contrôler appareils | 3 contrôleurs |
| **DataPersistenceService** | Sauvegarder données | serre.db (SQLite) |
| **LedController** | Logique LEDs | GPIO 27 |
| **HumidifierController** | Logique humidificateur | GPIO 26, 13 |
| **VentilationController** | Logique ventilation | GPIO 22 |
| **SerreOrchestrator** | Coordonner tout | Tous les services |

---

*Documentation simplifiée pour faciliter la maintenance*
