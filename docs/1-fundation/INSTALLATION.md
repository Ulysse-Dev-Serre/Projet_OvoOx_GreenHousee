# Guide d'installation et de configuration - Serre Connectée

## ✅ Prérequis complétés

- ✅ Python 3.11.2 installé
- ✅ pip3 installé
- ✅ Environnement virtuel `myenv` créé
- ✅ Dépendances installées depuis requirements.txt
- ✅ SQLite configuré (pas besoin d'installer PostgreSQL pour les tests)

## 🚀 Installation du service systemd

### Étape 1 : Copier le fichier service

```bash
sudo cp /home/ulysse/Projet_IoT_RaspberryPi/serre.service /etc/systemd/system/
```

### Étape 2 : Recharger systemd

```bash
sudo systemctl daemon-reload
```

### Étape 3 : Activer le service au démarrage

```bash
sudo systemctl enable serre.service
```

### Étape 4 : Démarrer le service

```bash
sudo systemctl start serre.service
```

## 📊 Commandes de gestion du service

### Vérifier l'état du service

```bash
sudo systemctl status serre.service
```

### Voir les logs en temps réel

```bash
# Logs systemd
sudo journalctl -u serre.service -f

# Logs de l'application (fichier)
tail -f /home/ulysse/Projet_IoT_RaspberryPi/data/logs/serre_controller.log
```

### Arrêter le service

```bash
sudo systemctl stop serre.service
```

### Redémarrer le service

```bash
sudo systemctl restart serre.service
```

### Désactiver le service

```bash
sudo systemctl disable serre.service
```

## 🧪 Tests avant activation du service

### Test 1 : Vérifier la configuration

```bash
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
export DB_ENV=prod

python -c "from src import config; print('Config OK:', config.DB_TYPE, config.HARDWARE_ENV)"
```

### Test 2 : Lancer manuellement (mode mock pour tester sans matériel)

```bash
# Test en mode mock (simulation)
export HARDWARE_ENV=mock
export DB_TYPE=sqlite
python main.py
```

Appuyez sur `Ctrl+C` pour arrêter.

### Test 3 : Lancer avec le vrai matériel

```bash
# Vérifier que les capteurs et actionneurs sont connectés
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
python main.py
```

### Test 4 : Vérifier la base de données

```bash
# Vérifier que la BD SQLite a été créée
ls -lh data/serre.db

# Interroger la base de données
sqlite3 data/serre.db "SELECT COUNT(*) FROM sensor_data;"
sqlite3 data/serre.db "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5;"
```

## 🌐 Lancer l'interface web (optionnel)

```bash
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
python src/api/app.py
```

Accéder à l'interface : http://IP_DU_RASPBERRY:5000

## 🔧 Configuration des variables d'environnement

Les variables sont définies dans le fichier `serre.service` :

- `HARDWARE_ENV` : `raspberry_pi` (matériel réel) ou `mock` (simulation)
- `DB_TYPE` : `sqlite` (base locale) ou `postgres` (PostgreSQL)
- `DB_ENV` : `prod` ou `test`
- `LOG_LEVEL` : `DEBUG`, `INFO`, `WARNING`, `ERROR`

Pour modifier, éditez le fichier service :

```bash
sudo nano /etc/systemd/system/serre.service
# Modifier les lignes Environment="..."
sudo systemctl daemon-reload
sudo systemctl restart serre.service
```

## 🗄️ Emplacement des fichiers

```
/home/ulysse/Projet_IoT_RaspberryPi/
├── data/
│   ├── serre.db                    # Base de données SQLite
│   ├── logs/
│   │   └── serre_controller.log    # Logs de l'application
│   └── user_settings.json          # Configuration utilisateur
├── myenv/                          # Environnement virtuel Python
├── src/                            # Code source
└── main.py                         # Point d'entrée
```

## 🐛 Dépannage

### Le service ne démarre pas

```bash
# Vérifier les erreurs
sudo journalctl -u serre.service -n 50 --no-pager

# Vérifier les permissions
ls -l /home/ulysse/Projet_IoT_RaspberryPi/main.py
ls -ld /home/ulysse/Projet_IoT_RaspberryPi/data/

# Créer les répertoires manquants
mkdir -p /home/ulysse/Projet_IoT_RaspberryPi/data/logs
```

### Erreur de capteur I2C (SCD30)

**Erreur "[Errno 121] Remote I/O error"**

Cette erreur signifie que le capteur est détecté mais ne répond pas correctement. 
Le code inclut maintenant une gestion automatique avec retry, mais si le problème persiste :

```bash
# 1. Vérifier que l'I2C est activé
sudo raspi-config
# -> Interface Options -> I2C -> Enable

# 2. Vérifier la détection du capteur
sudo i2cdetect -y 1
# Le SCD30 devrait apparaître à l'adresse 0x61

# 3. Tester avec le script de test
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
python test_hardware.py

# 4. Si le test fonctionne mais pas l'application :
# - Vérifier les connexions physiques
# - Redémarrer le Raspberry Pi
# - Augmenter les délais dans raspberry_pi.py
```

**Connexions SCD30 :**
- VIN → 3.3V ou 5V du Pi
- GND → GND du Pi  
- SCL → GPIO 3 (pin physique 5)
- SDA → GPIO 2 (pin physique 3)

### Permissions GPIO

```bash
# Ajouter l'utilisateur aux groupes nécessaires
sudo usermod -a -G gpio,i2c,spi ulysse

# Redémarrer pour appliquer
sudo reboot
```

### Base de données SQLite verrouillée

```bash
# Vérifier qu'une seule instance tourne
ps aux | grep python
sudo systemctl stop serre.service

# Si nécessaire, supprimer le fichier de verrou
rm -f /home/ulysse/Projet_IoT_RaspberryPi/data/serre.db-journal
```

## 📈 Surveillance du système

### Créer un script de monitoring

```bash
# Créer un script de vérification
cat > /home/ulysse/check_serre.sh << 'EOF'
#!/bin/bash
echo "=== État du service ==="
systemctl is-active serre.service

echo -e "\n=== Derniers logs (10 lignes) ==="
sudo journalctl -u serre.service -n 10 --no-pager

echo -e "\n=== Taille de la base de données ==="
ls -lh /home/ulysse/Projet_IoT_RaspberryPi/data/serre.db 2>/dev/null || echo "BD non créée"

echo -e "\n=== Nombre d'enregistrements ==="
sqlite3 /home/ulysse/Projet_IoT_RaspberryPi/data/serre.db \
  "SELECT COUNT(*) FROM sensor_data;" 2>/dev/null || echo "0"

echo -e "\n=== Dernière lecture ==="
sqlite3 /home/ulysse/Projet_IoT_RaspberryPi/data/serre.db \
  "SELECT timestamp, temperature, humidity, co2 FROM sensor_data ORDER BY timestamp DESC LIMIT 1;" \
  2>/dev/null || echo "Aucune donnée"
EOF

chmod +x /home/ulysse/check_serre.sh
```

Utilisation :

```bash
/home/ulysse/check_serre.sh
```

## 🔄 Migration vers PostgreSQL (optionnel, plus tard)

Quand vous voudrez migrer vers PostgreSQL :

1. Installer PostgreSQL
2. Créer la base de données
3. Modifier la variable d'environnement dans `serre.service` :
   ```
   Environment="DB_TYPE=postgres"
   ```
4. Redémarrer le service

## 📝 Notes importantes

- Le service se lance automatiquement au démarrage du Raspberry Pi
- Les logs sont dans `/var/log/journal/` (systemd) et `data/logs/`
- SQLite est suffisant pour ~1 an de données (à 60s d'intervalle)
- Pour un accès mobile, lancer aussi `src/api/app.py` ou créer un second service

---

*Dernière mise à jour : 30 septembre 2025*
