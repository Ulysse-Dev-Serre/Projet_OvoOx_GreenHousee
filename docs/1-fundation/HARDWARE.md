# Configuration Matérielle

Documentation complète du matériel utilisé dans le projet : capteurs, actionneurs, GPIO et câblage.

---

## 🔌 Vue d'Ensemble des Appareils

| Appareil | Type | GPIO | État ON | État OFF | Description |
|----------|------|------|---------|----------|-------------|
| **LEDs** | Relais | 27 | 0 | 1 | Éclairage pour les champignons |
| **Ventilateur humid** | Relais | 26 | 0 | 1 | Ventilateur de l'humidificateur |
| **Brumisateur** | Relais | 13 | 0 | 1 | Brumisateur ultrasonique |
| **Ventilation** | Relais | 22 | 0 | 1 | Ventilateur d'extraction |
| **Capteur SCD30** | I2C | - | - | - | Température, humidité, CO2 |

**⚠️ Important** : Les relais utilisent une **logique inverse** :
- GPIO = **0** → Relais activé (appareil ON)
- GPIO = **1** → Relais désactivé (appareil OFF)

---

## 📡 Capteur SCD30

### Caractéristiques

- **Type** : Capteur I2C
- **Mesures** : Température, humidité relative, CO2
- **Adresse I2C** : `0x61`
- **Fréquence de lecture** : 15 secondes
- **Plage CO2** : 400-10000 ppm
- **Plage température** : -40°C à +70°C
- **Plage humidité** : 0-100% RH

### Connexion

```
SCD30        Raspberry Pi
VIN    →     3.3V (Pin 1)
GND    →     GND (Pin 6)
SDA    →     SDA (GPIO 2, Pin 3)
SCL    →     SCL (GPIO 3, Pin 5)
```

### Vérification

```bash
# Vérifier que le capteur est détecté
sudo i2cdetect -y 1

# Résultat attendu :
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 60: -- 61 -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

### Code

Le capteur est lu via `hardware.lire_capteur()` dans :
- `src/hardware_interface/raspberry_pi.py` (mode réel)
- `src/hardware_interface/mock_hardware.py` (mode simulation)

---

## 💡 LEDs (GPIO 27)

### Spécifications

- **GPIO** : 27
- **Type** : Relais NO (Normalement Ouvert)
- **Tension** : 5V (via relais)
- **Logique** : Inverse (0 = ON, 1 = OFF)

### Connexion

```
Raspberry Pi → Relais → LEDs
GPIO 27      → IN1    → Alimentation 5V/12V
GND          → GND
5V           → VCC
```

### Contrôle

```python
# Allumer les LEDs
hardware.activer_leds()  # GPIO 27 → 0

# Éteindre les LEDs
hardware.desactiver_leds()  # GPIO 27 → 1
```

### Logique automatique

Fichier : `src/core/actuators/led_controller.py`

```
Si heure actuelle entre HEURE_DEBUT_LEDS et HEURE_FIN_LEDS
  → Allumer LEDs
Sinon
  → Éteindre LEDs
```

Par défaut : 9h - 20h (modifiable dans `data/user_settings.json`)

---

## 💧 Humidificateur (GPIO 26 + 13)

### Spécifications

L'humidificateur est composé de **2 appareils** :

| Composant | GPIO | Rôle |
|-----------|------|------|
| Ventilateur | 26 | Diffuse la brume |
| Brumisateur | 13 | Crée la brume ultrasonique |

Les deux doivent être activés **en même temps** pour fonctionner.

### Connexion

```
Raspberry Pi → Relais → Appareils
GPIO 26      → IN2    → Ventilateur (5V)
GPIO 13      → IN3    → Brumisateur (12V)
GND          → GND
5V           → VCC
```

### Contrôle

```python
# Allumer l'humidificateur
hardware.activer_humidificateur()
# → GPIO 26 → 0 (ventilateur ON)
# → GPIO 13 → 0 (brumisateur ON)

# Éteindre l'humidificateur
hardware.desactiver_humidificateur()
# → GPIO 26 → 1 (ventilateur OFF)
# → GPIO 13 → 1 (brumisateur OFF)
```

### Logique automatique

Fichier : `src/core/actuators/humidifier_controller.py`

```
Si humidité < SEUIL_HUMIDITE_ON (défaut: 75%)
  → Allumer humidificateur

Si humidité > SEUIL_HUMIDITE_OFF (défaut: 85%)
  → Éteindre humidificateur
```

**Hystérésis** : évite les allumages/extinctions rapides répétés.

---

## 🌬️ Ventilation (GPIO 22)

### Spécifications

- **GPIO** : 22
- **Type** : Relais NO (Normalement Ouvert)
- **Rôle** : Extraction d'air pour réduire le CO2
- **Tension** : 12V (via relais)
- **Logique** : Inverse (0 = ON, 1 = OFF)

### Connexion

```
Raspberry Pi → Relais → Ventilateur
GPIO 22      → IN4    → Ventilateur 12V
GND          → GND
5V           → VCC
```

### Contrôle

```python
# Allumer la ventilation
hardware.activer_ventilation()  # GPIO 22 → 0

# Éteindre la ventilation
hardware.desactiver_ventilation()  # GPIO 22 → 1
```

### Logique automatique

Fichier : `src/core/actuators/ventilation_controller.py`

```
Si CO2 > SEUIL_CO2_MAX (défaut: 1200 ppm)
  → Allumer ventilation
Sinon
  → Éteindre ventilation
```

---

## 🔧 Configuration des GPIO

### Modification des broches

**Fichier** : `src/config.py`

```python
# Broches GPIO (numérotation BCM)
PIN_LEDS = 27
PIN_VENTILATION = 22
PIN_FAN_HUMIDIFICATEUR = 26
PIN_BRUMISATEUR = 13
```

**⚠️ Attention** : Après modification, redémarrer l'application ou le service systemd.

### Numérotation BCM vs BOARD

Ce projet utilise la **numérotation BCM** (Broadcom).

Exemple :
- BCM 27 = BOARD 13
- BCM 22 = BOARD 15
- BCM 26 = BOARD 37
- BCM 13 = BOARD 33

📖 **Référence** : [Pinout Raspberry Pi](https://pinout.xyz)

---

## 🧪 Test Manuel du Matériel

### Script de test

```bash
python scripts/hardware_test_menu.py
```

Ce script permet de tester **individuellement** :
1. Capteur SCD30 (lecture température, humidité, CO2)
2. LEDs (allumer/éteindre)
3. Humidificateur (allumer/éteindre)
4. Ventilation (allumer/éteindre)

### Test via le menu CLI

Lancer l'application en mode réel :

```bash
export HARDWARE_ENV=raspberry_pi
python main.py
```

Commandes de test :
- `1` : Activer LEDs manuellement
- `2` : Désactiver LEDs manuellement
- `3` : Activer humidificateur manuellement
- `4` : Désactiver humidificateur manuellement
- `5` : Activer ventilation manuellement
- `6` : Désactiver ventilation manuellement
- `7` : Repasser en mode AUTO
- `8` : Arrêt d'urgence (tout OFF)

---

## 🐛 Dépannage Matériel

### Un appareil ne s'allume pas

**1. Vérifier le câblage**
- Relais alimenté en 5V ?
- GPIO correctement connecté à INx ?
- Masse commune (GND) ?

**2. Vérifier le relais**
```bash
# Forcer l'activation GPIO (test bas niveau)
gpio mode 27 out
gpio write 27 0  # Activer
gpio write 27 1  # Désactiver
```

**3. Vérifier les logs**
```bash
tail -f data/logs/serre_controller.log | grep GPIO
# Chercher : "GPIO 27 mis à 0" (activé) ou "GPIO 27 mis à 1" (désactivé)
```

### Le capteur SCD30 ne répond pas

**1. Vérifier I2C**
```bash
sudo i2cdetect -y 1
# Le capteur doit apparaître à 0x61
```

**2. Activer I2C (si désactivé)**
```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

**3. Vérifier les logs**
```bash
tail -f data/logs/serre_controller.log | grep SCD30
```

**4. Problème matériel ?**
- Vérifier alimentation 3.3V
- Vérifier câbles SDA/SCL
- Essayer un autre capteur

### Les relais cliquent mais l'appareil ne marche pas

**Causes possibles :**
- Mauvais câblage après le relais (NO/NC/COM)
- Appareil défectueux
- Tension insuffisante pour l'appareil

**Solution :**
Tester l'appareil **directement** avec son alimentation (sans relais).

---

## 📋 Schéma de Câblage Complet

```
┌──────────────────┐
│  Raspberry Pi    │
│                  │
│  GPIO 27  ───────┼───→ Relais 1 (IN1) → LEDs
│  GPIO 26  ───────┼───→ Relais 2 (IN2) → Ventilateur humid
│  GPIO 13  ───────┼───→ Relais 3 (IN3) → Brumisateur
│  GPIO 22  ───────┼───→ Relais 4 (IN4) → Ventilation
│                  │
│  SDA (GPIO 2) ───┼───→ SCD30 (SDA)
│  SCL (GPIO 3) ───┼───→ SCD30 (SCL)
│                  │
│  5V ─────────────┼───→ Relais (VCC)
│  3.3V ───────────┼───→ SCD30 (VIN)
│  GND ────────────┼───→ GND commun (Relais + SCD30)
└──────────────────┘
```

---

## 🔒 Sécurité

### Électrique

- **Isolation** : Les relais isolent le Raspberry Pi des charges électriques.
- **Tension** : Ne jamais connecter 12V/220V directement au Raspberry Pi.
- **Protection** : Utiliser des fusibles pour les charges importantes.

### Logicielle

- **État initial** : Tous les GPIO sont à 1 (OFF) au démarrage.
- **Arrêt propre** : Le `cleanup()` remet tous les GPIO à 1 (OFF) avant de quitter.
- **Mode mock** : Utilisez `HARDWARE_ENV=mock` pour développer sans risque.

---

## 📚 Références

- [Raspberry Pi GPIO Pinout](https://pinout.xyz)
- [lgpio Documentation](https://abyz.me.uk/lg/lgpio.html)
- [SCD30 Datasheet](https://www.sensirion.com/en/environmental-sensors/carbon-dioxide-sensors/carbon-dioxide-sensors-scd30/)
- [Adafruit CircuitPython SCD30](https://github.com/adafruit/Adafruit_CircuitPython_SCD30)
