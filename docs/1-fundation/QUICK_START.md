# 🚀 Quick Start - Serre Connectée

## ✅ Configuration actuelle

- ✅ Python 3.11.2 + environnement virtuel `myenv`
- ✅ Toutes les dépendances installées
- ✅ SQLite configuré (base de données légère, sans installation PostgreSQL)
- ✅ Service systemd prêt
- ✅ Tests effectués avec succès en mode mock

## 🏃 Démarrage rapide

### Option 1 : Test manuel (mode simulation)

```bash
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
export HARDWARE_ENV=mock
export DB_TYPE=sqlite
python main.py
```

Arrêter avec `Ctrl+C`.

### Option 2 : Test avec le matériel réel

```bash
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
python main.py
```

### Option 3 : Installation du service systemd (démarrage automatique)

```bash
# 1. Copier le fichier service
sudo cp serre.service /etc/systemd/system/

# 2. Recharger systemd
sudo systemctl daemon-reload

# 3. Activer au démarrage
sudo systemctl enable serre.service

# 4. Démarrer le service
sudo systemctl start serre.service

# 5. Vérifier l'état
sudo systemctl status serre.service

# 6. Voir les logs
sudo journalctl -u serre.service -f
```

## 📊 Vérifier les données

```bash
# Afficher les statistiques de la BD
python3 -c "
import sqlite3
conn = sqlite3.connect('data/serre.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM sensor_data')
print(f'Total enregistrements: {cur.fetchone()[0]}')
cur.execute('SELECT timestamp, temperature, humidity, co2 FROM sensor_data ORDER BY timestamp DESC LIMIT 5')
for row in cur.fetchall():
    print(row)
conn.close()
"
```

## 🌐 Interface web (optionnel)

```bash
cd /home/ulysse/Projet_IoT_RaspberryPi
source myenv/bin/activate
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
python src/api/app.py
```

Accès : `http://<IP_DU_RASPBERRY>:5000`

## 📁 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `INSTALLATION.md` | Guide d'installation détaillé |
| `REFACTORING_GUIDE.md` | Plan de refactorisation SOLID |
| `serre.service` | Fichier service systemd |
| `data/serre.db` | Base de données SQLite |
| `data/logs/serre_controller.log` | Logs de l'application |
| `data/user_settings.json` | Configuration utilisateur |

## 🔄 Prochaines étapes

1. **Tester avec le matériel réel** : Vérifier que capteurs et actionneurs fonctionnent
2. **Installer le service** : Pour démarrage automatique au boot
3. **Surveiller les logs** : Pendant 24h pour valider la stabilité
4. **Commencer la refactorisation** : Suivre `REFACTORING_GUIDE.md`

## 🆘 Commandes utiles

```bash
# État du service
sudo systemctl status serre.service

# Redémarrer
sudo systemctl restart serre.service

# Arrêter
sudo systemctl stop serre.service

# Logs en temps réel
sudo journalctl -u serre.service -f

# Logs application
tail -f data/logs/serre_controller.log

# Taille BD
ls -lh data/serre.db
```

---

**Système prêt à l'emploi !** 🎉
