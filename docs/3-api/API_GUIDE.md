# 🌐 Guide de l'API REST - Simple et Pratique

## Vue d'ensemble

L'API permet de contrôler et surveiller la serre depuis n'importe quelle application (mobile, desktop).

**Adresse :** `http://10.0.0.216:5000`

## 📖 Documentation interactive (Swagger)

La meilleure façon d'explorer l'API est d'utiliser Swagger :

**Ouvrez dans votre navigateur :**
```
http://10.0.0.216:5000/docs
```

Vous pourrez :
- ✅ Voir tous les endpoints
- ✅ Tester directement dans le navigateur
- ✅ Voir les exemples de requêtes/réponses

## 🚀 Démarrer l'API

```bash
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
python src/api/monitoring_api.py
```

L'API démarre sur le port **5000**.

## 📡 Endpoints disponibles

### 1. Vérifier que l'API fonctionne

**Endpoint :** `GET /`

**Commande :**
```bash
curl http://10.0.0.216:5000/
```

**Réponse :**
```json
{
  "name": "Serre Connectée API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "status": "/api/status",
    "settings": "/api/settings",
    ...
  }
}
```

---

### 2. Obtenir l'état actuel de la serre

**Endpoint :** `GET /api/status`

**Ce que ça fait :** Retourne température, humidité, CO2 et état des appareils

**Commande :**
```bash
curl http://10.0.0.216:5000/api/status
```

**Réponse :**
```json
{
  "timestamp": "2025-09-30 02:09:42",
  "temperature": "30.1",
  "humidite": "35.9",
  "co2": "753",
  "sensor_read_ok": true,
  "leds": {
    "is_active": false,
    "manual_mode": false
  },
  "humidifier": {
    "is_active": false,
    "manual_mode": false
  },
  "ventilation": {
    "is_active": false,
    "manual_mode": false
  }
}
```

**Utilisation dans votre app :**
- Appelez cet endpoint toutes les 5-10 secondes pour rafraîchir l'affichage
- Affichez `temperature`, `humidite`, `co2`
- Montrez l'état des appareils (ON/OFF, AUTO/MANUEL)

---

### 3. Obtenir la configuration

**Endpoint :** `GET /api/settings`

**Ce que ça fait :** Retourne tous les paramètres (horaires, seuils)

**Commande :**
```bash
curl http://10.0.0.216:5000/api/settings
```

**Réponse :**
```json
{
  "HEURE_DEBUT_LEDS": 9,
  "HEURE_FIN_LEDS": 20,
  "SEUIL_HUMIDITE_ON": 75.0,
  "SEUIL_HUMIDITE_OFF": 84.9,
  "SEUIL_CO2_MAX": 1200.0,
  ...
}
```

---

### 4. Modifier la configuration

**Endpoint :** `PUT /api/settings`

**Ce que ça fait :** Change les paramètres (horaires, seuils)

**Commande :**
```bash
curl -X PUT http://10.0.0.216:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "HEURE_DEBUT_LEDS": 8,
      "SEUIL_HUMIDITE_ON": 70.0
    }
  }'
```

**Réponse :**
```json
{
  "success": true,
  "message": "Paramètres mis à jour",
  "settings": { ... }
}
```

---

### 5. Contrôler les LEDs manuellement

**Endpoint :** `POST /api/control/leds`

**Ce que ça fait :** Active ou désactive les LEDs en mode manuel

**Commandes :**
```bash
# Activer les LEDs
curl -X POST http://10.0.0.216:5000/api/control/leds \
  -H "Content-Type: application/json" \
  -d '{"active": true, "state": true}'

# Désactiver les LEDs
curl -X POST http://10.0.0.216:5000/api/control/leds \
  -H "Content-Type: application/json" \
  -d '{"active": true, "state": false}'
```

**Réponse :**
```json
{
  "success": true,
  "device": "leds",
  "manual_mode": true,
  "state": true
}
```

---

### 6. Contrôler l'humidificateur

**Endpoint :** `POST /api/control/humidifier`

**Même principe que les LEDs**

```bash
# Activer
curl -X POST http://10.0.0.216:5000/api/control/humidifier \
  -H "Content-Type: application/json" \
  -d '{"active": true, "state": true}'
```

---

### 7. Contrôler la ventilation

**Endpoint :** `POST /api/control/ventilation`

**Même principe que les LEDs**

```bash
# Activer
curl -X POST http://10.0.0.216:5000/api/control/ventilation \
  -H "Content-Type: application/json" \
  -d '{"active": true, "state": true}'
```

---

### 8. Remettre en mode automatique

**Endpoint :** `POST /api/control/auto`

**Ce que ça fait :** Désactive le mode manuel pour TOUS les appareils

**Commande :**
```bash
curl -X POST http://10.0.0.216:5000/api/control/auto
```

**Réponse :**
```json
{
  "success": true,
  "message": "Mode automatique activé pour tous les actionneurs"
}
```

---

### 9. Arrêt d'urgence

**Endpoint :** `POST /api/control/emergency_stop`

**Ce que ça fait :** Éteint immédiatement TOUS les appareils

**Commande :**
```bash
curl -X POST http://10.0.0.216:5000/api/control/emergency_stop
```

**Réponse :**
```json
{
  "success": true,
  "message": "Arrêt d'urgence effectué"
}
```

---

### 10. Health check

**Endpoint :** `GET /health`

**Ce que ça fait :** Vérifie que l'API fonctionne

**Commande :**
```bash
curl http://10.0.0.216:5000/health
```

**Réponse :**
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

## 🖥️ Développer une Application Frontend

📖 **Guide complet pour connecter votre frontend** : [FRONTEND_CONNECT.md](../FRONTEND_CONNECT.md)

Ce guide contient :
- Tous les endpoints nécessaires
- Exemples de code (JavaScript, Python, Flutter)
- Layout d'interface recommandé
- Gestion des erreurs
- Checklist de développement

## 🧪 Tester l'API rapidement

### Depuis le terminal du Raspberry Pi

```bash
# État actuel
curl http://localhost:5000/api/status | python3 -m json.tool

# Configuration
curl http://localhost:5000/api/settings | python3 -m json.tool

# Activer LEDs
curl -X POST http://localhost:5000/api/control/leds \
  -H "Content-Type: application/json" \
  -d '{"active": true, "state": true}'

# Mode auto
curl -X POST http://localhost:5000/api/control/auto
```

### Depuis votre PC (sur le même réseau)

Remplacez `localhost` par `10.0.0.216`

```bash
curl http://10.0.0.216:5000/api/status
```

## 📝 Format des requêtes

### Contrôle d'appareil (LEDs, humidificateur, ventilation)

**Body JSON :**
```json
{
  "active": true,    // true = mode manuel, false = mode auto
  "state": true      // true = ON, false = OFF (si mode manuel)
}
```

**Exemples :**
- Mode manuel ON : `{"active": true, "state": true}`
- Mode manuel OFF : `{"active": true, "state": false}`
- Mode auto : `{"active": false}` (state ignoré)

### Modification de configuration

**Body JSON :**
```json
{
  "settings": {
    "HEURE_DEBUT_LEDS": 8,
    "HEURE_FIN_LEDS": 22,
    "SEUIL_CO2_MAX": 1500
  }
}
```

## ⚙️ Configuration de l'API

**Fichier :** `src/config.py`

```python
APP_HOST = '0.0.0.0'  # Écoute sur toutes les interfaces
APP_PORT = 5000       # Port de l'API
```

**Variables d'environnement :**
```bash
export HARDWARE_ENV=raspberry_pi  # ou 'mock' pour tests
export DB_TYPE=sqlite              # ou 'postgres' plus tard
export LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

## 🔒 Sécurité (à venir)

Pour l'instant, l'API est **ouverte** (pas d'authentification).

**Pour la production, ajouter :**
- Authentification JWT
- Rate limiting
- HTTPS
- Restriction des origins CORS

---

*Guide simple pour utiliser l'API de la serre*
