# Commandes Utiles

Toutes les commandes utiles pour gérer le projet au quotidien.


## Lancement de l'Application

### Mode Mock (Simulation)

```bash
export HARDWARE_ENV=mock
export DB_TYPE=sqlite
python main.py
```

### Mode Réel (Matériel Connecté)

```bash
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
python main.py
```

### Avec l'API Activée

```bash
export API_KEY="votre-cle-secrete"
export HARDWARE_ENV=raspberry_pi
python main.py
```

### Tout en une ligne

```bash
HARDWARE_ENV=raspberry_pi DB_TYPE=sqlite API_KEY="test-key" python main.py
```

---

## Gestion du Service Systemd

### Démarrage/Arrêt

```bash
# Démarrer le service
sudo systemctl start serre.service

# Arrêter le service
sudo systemctl stop serre.service

# Redémarrer le service
sudo systemctl restart serre.service

# Voir l'état du service
sudo systemctl status serre.service
```

### Activation/Désactivation au démarrage

```bash
# Activer au boot
sudo systemctl enable serre.service

# Désactiver au boot
sudo systemctl disable serre.service
```

### Logs

```bash
# Voir les logs en temps réel
sudo journalctl -u serre.service -f

# Voir les 100 dernières lignes
sudo journalctl -u serre.service -n 100

# Voir les logs depuis aujourd'hui
sudo journalctl -u serre.service --since today

# Voir les logs d'une période
sudo journalctl -u serre.service --since "2025-09-30 14:00" --until "2025-09-30 16:00"
```

### Modifier le Service

```bash
# Éditer le fichier service
sudo nano /etc/systemd/system/serre.service

# Recharger après modification
sudo systemctl daemon-reload

# Redémarrer pour appliquer
sudo systemctl restart serre.service
```

---

## Gestion des Processus Python

### Arrêter tous les processus Python liés au projet

```bash
# Utiliser le script fourni
bash scripts/stop_all.sh

# Ou manuellement
pkill -f "python main.py"

# Ou forcer l'arrêt (⚠️ ne fait pas le cleanup GPIO)
pkill -9 -f "python main.py"
```

### ⚠️ Arrêt d'urgence des GPIO

Si vous avez tué brutalement le processus et que les actionneurs restent allumés :

```bash
# Éteindre tous les GPIO (27, 26, 13, 22)
python scripts/emergency_gpio_off.py
```

### Trouver les processus en cours

```bash
# Voir tous les processus Python
ps aux | grep python

# Voir les processus sur le port 5000 (API)
lsof -ti:5000

# Tuer un processus sur le port 5000
lsof -ti:5000 | xargs kill -9
```

---

## Base de Données

### SQLite (Par défaut)

```bash
# Voir la base de données
sqlite3 data/serre.db

# Dans sqlite3, voir les tables
.tables

# Voir le schéma
.schema sensor_data

# Voir les dernières données
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;

# Quitter sqlite3
.quit
```

### Supprimer la base SQLite

```bash
rm data/serre.db
# Elle sera recréée automatiquement au prochain démarrage
```


**Variables d'environnement pour PostgreSQL** :

```bash
export DB_TYPE=postgres
export DB_ENV=prod
export DB_USER_PROD="ulysse"
export DB_PASSWORD_PROD="votre_mot_de_passe"
export DB_HOST_PROD="localhost"
export DB_NAME_PROD="serre_connectee"
```

---

## Tests

### Tests unitaires (pytest)

```bash
# Lancer tous les tests
pytest

# Lancer les tests avec sortie détaillée
pytest -v

# Lancer un test spécifique
pytest tests/core/test_serre_logic.py

# Voir la couverture
pytest --cov=src tests/
```

### Tests de l'API

```bash
# Test rapide avec bash
bash scripts/test_api.sh

# Test détaillé avec Python
python scripts/test_api_simple.py

# Avec IP et clé personnalisées
bash scripts/test_api.sh http://192.168.1.100:5000 ma-cle
python scripts/test_api_simple.py http://192.168.1.100:5000 ma-cle
```

---

## API FastAPI

### Accéder à l'API

```bash
# Documentation interactive (Swagger)
http://<IP_RASPBERRY>:5000/docs

# Health check
curl http://localhost:5000/health

# Status (sans authentification)
curl http://localhost:5000/api/status

# Contrôle LEDs (avec authentification)
curl -X POST http://localhost:5000/api/control/leds \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{"manual_mode": true, "state": true}'
```

### Variables d'environnement API

```bash
export API_KEY="votre-cle-secrete"        # Clé pour authentification
export APP_HOST="0.0.0.0"                  # Host API (défaut: 0.0.0.0)
export APP_PORT=5000                       # Port API (défaut: 5000)
```

---

## Logs

### Voir les logs de l'application

```bash
# Logs en temps réel
tail -f data/logs/serre_controller.log

# Dernières 100 lignes
tail -n 100 data/logs/serre_controller.log

# Chercher des erreurs
grep ERROR data/logs/serre_controller.log

# Chercher des warnings
grep WARNING data/logs/serre_controller.log
```

### Supprimer les anciens logs

```bash
# Supprimer les logs
rm data/logs/serre_controller.log

# Rotation des logs (si trop volumineux)
mv data/logs/serre_controller.log data/logs/serre_controller.log.old
```

---



## Réseau

### Trouver l'IP du Raspberry Pi

```bash
# Toutes les interfaces
ip addr show

# Juste l'IP locale
hostname -I

# Détails réseau
ifconfig
```

### Tester la connectivité

```bash
# Ping depuis un autre appareil
ping <IP_RASPBERRY>

# Tester le port API
telnet <IP_RASPBERRY> 5000

# Ou avec curl
curl http://<IP_RASPBERRY>:5000/health
```

---

## Matériel

### Test manuel du matériel

```bash
python scripts/hardware_test_menu.py
```

Ce script permet de tester individuellement tous les capteurs et actionneurs.

📖 **Détails matériels** : [HARDWARE.md](HARDWARE.md)

---

## Divers

### Mettre à jour le Raspberry Pi

```bash
sudo apt update
sudo apt upgrade -y
```

### Redémarrer le Raspberry Pi

```bash
sudo reboot
```

### Arrêter le Raspberry Pi

```bash
sudo shutdown -h now
```


