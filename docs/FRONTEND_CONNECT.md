# Frontend Connection Guide

Guide minimaliste pour connecter **n'importe quelle application frontend** (Electron, Flutter, React, Vue, etc.) au backend de la serre.

---

## 🎯 Informations Essentielles

**URL de base** : `http://<IP_RASPBERRY>:5000`

**Authentification** : Header `X-API-Key: votre-cle`

**Fréquence de polling** : 5-10 secondes

---

## 📊 Affichages Nécessaires

### Données en Temps Réel

| Affichage | Source | Endpoint | Clé JSON | Plage de valeurs |
|-----------|--------|----------|----------|------------------|
| **Température** | Capteur SCD30 | `GET /api/status` | `temperature` | -10°C à 50°C |
| **Humidité** | Capteur SCD30 | `GET /api/status` | `humidite` | 0% à 100% |
| **CO2** | Capteur SCD30 | `GET /api/status` | `co2` | 400 à 5000 ppm |
| **Date/Heure dernière lecture** | Système | `GET /api/status` | `timestamp` | Format: `YYYY-MM-DD HH:MM:SS` |

**⚠️ Gestion des erreurs capteurs** :
- Si un capteur est défaillant, la valeur peut être `null` ou `"N/A"`
- Vérifier `sensor_read_ok: false` pour détecter un problème

### État des Actionneurs

Chaque actionneur a 4 informations :

| Actionneur | État ON/OFF | Mode AUTO/MANUEL | Durée ON | Durée OFF |
|------------|-------------|------------------|----------|-----------|
| **LEDs** | `leds.is_active` | `leds.manual_mode` | `leds.on_duration_seconds` | `leds.off_duration_seconds` |
| **Humidificateur** | `humidifier.is_active` | `humidifier.manual_mode` | `humidifier.on_duration_seconds` | `humidifier.off_duration_seconds` |
| **Ventilation** | `ventilation.is_active` | `ventilation.manual_mode` | `ventilation.on_duration_seconds` | `ventilation.off_duration_seconds` |

**Endpoint** : `GET /api/status`

**Exemple d'affichage** :
- LED : 🟢 ON (AUTO) - Allumée depuis 3600s (1h)
- LED : 🟢 ON (MANUEL) - Allumée depuis 120s
- LED : 🔴 OFF (AUTO) - Éteinte depuis 7200s (2h)

**Utilité des durées** :
- Détecter des problèmes (ex: ventilation OFF depuis >23h = capteur CO2 défaillant ?)
- Analyser le comportement (ex: humidificateur ON trop longtemps = fuite ?)

---

## 🎛️ Contrôles (Boutons)

### Contrôle Manuel des Actionneurs

| Bouton | Action | Endpoint | Méthode | Body JSON | Auth |
|--------|--------|----------|---------|-----------|------|
| **Allumer LEDs** | Active manuellement | `/api/control/leds` | POST | `{"manual_mode": true, "state": true}` | ✅ |
| **Éteindre LEDs** | Désactive manuellement | `/api/control/leds` | POST | `{"manual_mode": true, "state": false}` | ✅ |
| **Allumer Humidificateur** | Active manuellement | `/api/control/humidifier` | POST | `{"manual_mode": true, "state": true}` | ✅ |
| **Éteindre Humidificateur** | Désactive manuellement | `/api/control/humidifier` | POST | `{"manual_mode": true, "state": false}` | ✅ |
| **Allumer Ventilation** | Active manuellement | `/api/control/ventilation` | POST | `{"manual_mode": true, "state": true}` | ✅ |
| **Éteindre Ventilation** | Désactive manuellement | `/api/control/ventilation` | POST | `{"manual_mode": true, "state": false}` | ✅ |
| **Mode AUTO (Tout)** | Repasse tout en auto | `/api/control/auto` | POST | (vide) | ✅ |
| **Arrêt d'Urgence** | Éteint tout immédiatement | `/api/control/emergency_stop` | POST | (vide) | ✅ |

**Note** : Le mode manuel désactive l'automatisation. Pour réactiver l'automatisation, utiliser le bouton "Mode AUTO".

### Format des Réponses de Contrôle

Tous les endpoints de contrôle retournent le même format :

```json
{
  "success": true,
  "actuator": "leds",
  "manual_mode": true,
  "state": true
}
```

Pour `/api/control/auto` et `/api/control/emergency_stop` :
```json
{
  "success": true,
  "message": "Tous les actionneurs sont en mode automatique",
  "status": {
    "timestamp": "2025-09-30 18:30:00",
    "temperature": "25.5",
    "humidite": "80.2",
    "co2": "950",
    "sensor_read_ok": true,
    "leds": {
      "is_active": false,
      "manual_mode": false,
      "on_duration_seconds": 0,
      "off_duration_seconds": 3600.5
    },
    "humidifier": {
      "is_active": true,
      "manual_mode": false,
      "on_duration_seconds": 1200.0,
      "off_duration_seconds": 0
    },
    "ventilation": {
      "is_active": false,
      "manual_mode": false,
      "on_duration_seconds": 0,
      "off_duration_seconds": 7200.0
    }
  }
}
```

**Note** : Le champ `status` contient l'état complet du système après l'action.

---

## ⚙️ Configuration (Inputs)

### Paramètres Modifiables

| Input | Description | Clé JSON | Type | Valeur par défaut |
|-------|-------------|----------|------|-------------------|
| **Heure début LEDs** | Heure d'allumage auto des LEDs | `HEURE_DEBUT_LEDS` | number | 9 |
| **Heure fin LEDs** | Heure d'extinction auto des LEDs | `HEURE_FIN_LEDS` | number | 20 |
| **Seuil humidité ON** | Active humidificateur si < | `SEUIL_HUMIDITE_ON` | float | 75.0 |
| **Seuil humidité OFF** | Désactive humidificateur si > | `SEUIL_HUMIDITE_OFF` | float | 84.9 |
| **Seuil CO2 MAX** | Active ventilation si > | `SEUIL_CO2_MAX` | float | 1200.0 |
| **Heure début opération** | Début période humidificateur/ventilation | `HEURE_DEBUT_JOUR_OPERATION` | number | 8 |
| **Heure fin opération** | Fin période humidificateur/ventilation | `HEURE_FIN_JOUR_OPERATION` | number | 22 |

### Lire la Configuration

**Endpoint** : `GET /api/settings`

**Réponse** :
```json
{
  "HEURE_DEBUT_LEDS": 9,
  "HEURE_FIN_LEDS": 20,
  "SEUIL_HUMIDITE_ON": 75.0,
  "SEUIL_HUMIDITE_OFF": 84.9,
  "SEUIL_CO2_MAX": 1200.0,
  "HEURE_DEBUT_JOUR_OPERATION": 8,
  "HEURE_FIN_JOUR_OPERATION": 22
}
```

### Modifier la Configuration

**Endpoint** : `PUT /api/settings`

**Authentification** : ✅ Requise

**Body JSON** :
```json
{
  "settings": {
    "HEURE_DEBUT_LEDS": 8,
    "SEUIL_HUMIDITE_ON": 70.0
  }
}
```

**Réponse** :
```json
{
  "success": true,
  "message": "Paramètres mis à jour avec succès",
  "new_settings": { ... }
}
```

---

## 📈 Historique (Optionnel)

### Récupérer l'Historique

**Endpoint** : `GET /api/history?limit=100`

**Paramètres** :
- `limit` : Nombre d'entrées (défaut: 100)

**Réponse** :
```json
{
  "count": 100,
  "data": [
    {
      "timestamp": "2025-09-30 14:30:00",
      "temperature": 22.5,
      "humidity": 80.2,
      "co2": 950,
      "leds_active": true,
      "humidifier_active": true,
      "ventilation_active": false
    }
  ]
}
```

**Utilisation** : Graphiques, tableaux, export CSV

---

## 🔐 Authentification

### Configuration

Sur le Raspberry Pi :
```bash
export API_KEY="votre-cle-secrete"
python main.py
```

### Dans votre Frontend

Ajouter le header à **toutes les requêtes de contrôle** :

```
X-API-Key: votre-cle-secrete
```

**Endpoints nécessitant l'authentification** :
- POST `/api/control/*` (tous les contrôles)
- PUT `/api/settings` (modification config)

**Endpoints SANS authentification** :
- GET `/api/status` (lecture état)
- GET `/api/settings` (lecture config)
- GET `/api/history` (lecture historique)
- GET `/health` (health check)

---

## 🎨 Exemple d'Interface Minimale

### Layout Recommandé

```
┌────────────────────────────────────────┐
│  🌱 SERRE CONNECTÉE                    │
├────────────────────────────────────────┤
│  📊 DONNÉES                            │
│  Température: 25.5°C                   │
│  Humidité: 80%                         │
│  CO2: 950 ppm                          │
│  Dernière lecture: 16:30:00            │
├────────────────────────────────────────┤
│  💡 LEDs          🟢 ON    [AUTO]     │
│     [Allumer] [Éteindre] [Mode AUTO]  │
│                                        │
│  💧 Humidificateur 🟢 ON   [AUTO]     │
│     [Allumer] [Éteindre] [Mode AUTO]  │
│                                        │
│  🌬️ Ventilation    🔴 OFF  [AUTO]     │
│     [Allumer] [Éteindre] [Mode AUTO]  │
├────────────────────────────────────────┤
│  ⚙️ CONFIGURATION                      │
│  LEDs ON: [9]h  OFF: [20]h            │
│  Humidité ON: [75]%  OFF: [85]%       │
│  CO2 MAX: [1200] ppm                   │
│  [Enregistrer]                         │
├────────────────────────────────────────┤
│  🚨 [ARRÊT D'URGENCE]                  │
└────────────────────────────────────────┘
```

---

## 💻 Exemple de Code

### Fetch Status (Toutes les 10 secondes)

```javascript
async function fetchStatus() {
  const response = await fetch('http://192.168.1.100:5000/api/status');
  const data = await response.json();
  
  // Vérifier si les capteurs fonctionnent
  if (!data.sensor_read_ok) {
    document.getElementById('sensor-alert').style.display = 'block';
  }
  
  // Mettre à jour l'affichage (gérer N/A)
  document.getElementById('temperature').textContent = 
    data.temperature === "N/A" ? "---" : data.temperature + '°C';
  document.getElementById('humidity').textContent = 
    data.humidite === "N/A" ? "---" : data.humidite + '%';
  document.getElementById('co2').textContent = 
    data.co2 === "N/A" ? "---" : data.co2 + ' ppm';
  document.getElementById('timestamp').textContent = data.timestamp;
  
  // État LEDs
  document.getElementById('leds-status').textContent = 
    data.leds.is_active ? '🟢 ON' : '🔴 OFF';
  document.getElementById('leds-mode').textContent = 
    data.leds.manual_mode ? 'MANUEL' : 'AUTO';
  
  // Durées (utile pour diagnostics)
  const ledsOnDuration = data.leds.on_duration_seconds || 0;
  const ledsOffDuration = data.leds.off_duration_seconds || 0;
  document.getElementById('leds-on-duration').textContent = 
    ledsOnDuration > 0 ? `Allumée depuis ${Math.floor(ledsOnDuration)}s` : '';
  document.getElementById('leds-off-duration').textContent = 
    ledsOffDuration > 0 ? `Éteinte depuis ${Math.floor(ledsOffDuration)}s` : '';
    
  // Répéter pour humidifier et ventilation
  
  // Alerte si ventilation OFF depuis >23h (82800s)
  if (!data.ventilation.is_active && data.ventilation.off_duration_seconds > 82800) {
    document.getElementById('ventilation-alert').style.display = 'block';
    document.getElementById('ventilation-alert').textContent = 
      '⚠️ Ventilation éteinte depuis >23h - Vérifier capteur CO2';
  }
}

// Polling
setInterval(fetchStatus, 10000);
fetchStatus(); // Premier appel immédiat
```

### Contrôle LEDs

```javascript
const API_KEY = 'votre-cle-secrete';
const BASE_URL = 'http://192.168.1.100:5000';

async function toggleLeds(on) {
  await fetch(`${BASE_URL}/api/control/leds`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      manual_mode: true,
      state: on
    })
  });
}

// Utilisation
document.getElementById('btn-leds-on').onclick = () => toggleLeds(true);
document.getElementById('btn-leds-off').onclick = () => toggleLeds(false);
```

### Mode AUTO

```javascript
async function setAutoMode() {
  await fetch(`${BASE_URL}/api/control/auto`, {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY }
  });
}

document.getElementById('btn-auto').onclick = setAutoMode;
```

### Modifier Configuration

```javascript
async function saveSettings() {
  const settings = {
    HEURE_DEBUT_LEDS: parseInt(document.getElementById('led-start').value),
    HEURE_FIN_LEDS: parseInt(document.getElementById('led-end').value),
    SEUIL_HUMIDITE_ON: parseFloat(document.getElementById('humidity-on').value),
    SEUIL_HUMIDITE_OFF: parseFloat(document.getElementById('humidity-off').value),
    SEUIL_CO2_MAX: parseFloat(document.getElementById('co2-max').value)
  };
  
  const response = await fetch(`${BASE_URL}/api/settings`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({ settings })
  });
  
  const result = await response.json();
  alert(result.message);
}

document.getElementById('btn-save').onclick = saveSettings;
```

### Arrêt d'Urgence

```javascript
async function emergencyStop() {
  if (!confirm('⚠️ Arrêter tous les appareils ?')) return;
  
  await fetch(`${BASE_URL}/api/control/emergency_stop`, {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY }
  });
  
  alert('🚨 Arrêt d\'urgence effectué');
}

document.getElementById('btn-emergency').onclick = emergencyStop;
```

---

## 🐛 Gestion des Erreurs

### Codes HTTP

| Code | Signification | Action recommandée |
|------|---------------|-------------------|
| **200** | Succès | Traiter la réponse normalement |
| **400** | Requête invalide | Vérifier le format JSON |
| **401** | Clé API invalide | Vérifier `X-API-Key` |
| **404** | Endpoint introuvable | Vérifier l'URL |
| **500** | Erreur serveur | Réessayer après 30s |
| **503** | Service non disponible | Orchestrateur non attaché, relancer main.py |

### États d'Erreur des Capteurs

Si un capteur est défaillant, la réponse `/api/status` peut contenir :

```json
{
  "timestamp": "2025-09-30 14:30:00",
  "temperature": "N/A",
  "humidite": "N/A",
  "co2": "N/A",
  "sensor_read_ok": false
}
```

**Gestion dans l'UI** :
- Afficher "N/A" ou "---" au lieu de la valeur
- Afficher une alerte "❌ Capteur défaillant"
- Désactiver les graphiques tant que `sensor_read_ok: false`

### Vérifier la Connexion

```javascript
async function checkConnection() {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Connexion échouée:', error);
    return false;
  }
}
```

### Gérer les Erreurs HTTP

```javascript
async function safeRequest(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (response.status === 401) {
      alert('❌ Clé API invalide');
      return null;
    }
    
    if (response.status === 503) {
      alert('❌ Service non disponible');
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Erreur requête:', error);
    alert('❌ Erreur de connexion');
    return null;
  }
}
```

---

## 📋 Checklist Développement

### Étape 1 : Configuration
- [ ] IP du Raspberry Pi : `10.0.0.216`
- [ ] Configurer `API_KEY = 'test-key'` dans l'app
- [ ] Tester la connexion (`GET /health`)

### Étape 2 : Affichage
- [ ] Afficher température, humidité, CO2
- [ ] Afficher état des 3 actionneurs (ON/OFF + AUTO/MANUEL)
- [ ] Mettre à jour toutes les 10 secondes

### Étape 3 : Contrôles
- [ ] Boutons ON/OFF pour chaque actionneur
- [ ] Bouton "Mode AUTO"
- [ ] Bouton "Arrêt d'urgence"

### Étape 4 : Configuration
- [ ] Inputs pour les 5 paramètres
- [ ] Charger les valeurs actuelles au démarrage
- [ ] Bouton "Enregistrer"

### Étape 5 : UX
- [ ] Indicateurs visuels clairs (🟢/🔴)
- [ ] Feedback utilisateur (toasts, alerts)
- [ ] Gestion des erreurs (codes HTTP, capteurs défaillants)
- [ ] Confirmation pour arrêt d'urgence
- [ ] Afficher "---" si capteur défaillant

### Étape 6 : Optionnel
- [ ] Graphiques historiques
- [ ] Export CSV
- [ ] Notifications push
- [ ] Mode hors ligne

---

## 🌐 CORS & Electron

Pour Electron, le CORS est déjà configuré côté serveur.

Si vous avez des problèmes, vérifier dans `src/api/monitoring_api.py` :

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    # Ajouter votre origin si besoin
]
```

---

## 🧪 Tester l'API

### Option 1 : Script Bash (Rapide)

```bash
bash scripts/test_api.sh
# ou avec IP personnalisée
bash scripts/test_api.sh http://192.168.1.100:5000 votre-cle
```

**Ce que ça teste** :
- ✅ Health check
- ✅ Status avec durées (on_duration, off_duration)
- ✅ Settings avec 7 paramètres
- ✅ Authentification (avec et sans token)
- ✅ Contrôles (LEDs, mode AUTO)

### Option 2 : Script Python (Détaillé)

```bash
python scripts/test_api_simple.py
# ou avec IP personnalisée
python scripts/test_api_simple.py http://192.168.1.100:5000 votre-cle
```

### Option 3 : Swagger UI (Interactif)

Ouvrez dans votre navigateur : `http://<IP_RASPBERRY>:5000/docs`

---

## 📚 Références

- **API complète** : `http://10.0.0.216:5000/docs` (Swagger)
- **Code backend** : `src/api/monitoring_api.py`
- **Tests curl** : `docs/3-api/API_GUIDE.md`
- **Scripts de test** : `scripts/test_api.sh` et `scripts/test_api_simple.py`

---

**Ce guide contient TOUT ce dont vous avez besoin pour développer un frontend fonctionnel.**
