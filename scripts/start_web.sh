#!/bin/bash
# Script pour démarrer l'API de monitoring (FastAPI) de la serre

echo "🌐 Démarrage de l'API de Monitoring - Serre Connectée"
echo "=========================================================="

# Répertoire du projet
PROJECT_DIR="/home/ulysse/Projet_IoT_RaspberryPi"
cd "$PROJECT_DIR" || exit 1

# Arrêter l'API si elle tourne déjà
if pgrep -f "python.*monitoring_api.py" > /dev/null; then
    echo "🛑 Arrêt de l'API existante..."
    pkill -f "python.*monitoring_api.py" 2>/dev/null
    sleep 2
    echo "✅ API arrêtée"
fi

# Activer l'environnement virtuel
echo "🐍 Activation de l'environnement virtuel..."
source myenv/bin/activate

# Variables d'environnement
export HARDWARE_ENV=raspberry_pi
export DB_TYPE=sqlite
export LOG_LEVEL=INFO

# Obtenir l'IP locale
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "✅ Environnement configuré :"
echo "   - HARDWARE_ENV: $HARDWARE_ENV"
echo "   - DB_TYPE: $DB_TYPE"
echo "   - LOG_LEVEL: $LOG_LEVEL"
echo ""
echo "🚀 Démarrage de l'API de monitoring (READ-ONLY)..."
echo ""

# Démarrer l'API
python src/api/monitoring_api.py &
API_PID=$!

# Attendre que l'API démarre
sleep 3

# Vérifier que l'API tourne
if ps -p $API_PID > /dev/null 2>&1; then
    echo "=========================================================="
    echo "✅ API de monitoring démarrée avec succès !"
    echo ""
    echo "📱 Accès à l'API :"
    echo "   - Local:   http://localhost:5000/docs"
    echo "   - Réseau:  http://$LOCAL_IP:5000/docs"
    echo ""
    echo "⚠️  Mode READ-ONLY : L'API lit SQLite uniquement"
    echo "   Pour contrôler les appareils, utilisez le CLI menu de main.py"
    echo ""
    echo "🛑 Pour arrêter l'API :"
    echo "   pkill -f 'python src/api/monitoring_api.py'"
    echo "   ou: kill $API_PID"
    echo ""
    echo "📋 Logs en temps réel :"
    echo "   tail -f data/logs/serre_controller.log"
    echo "=========================================================="
else
    echo "❌ Échec du démarrage de l'API"
    echo "Vérifiez les logs dans data/logs/serre_controller.log"
    exit 1
fi
