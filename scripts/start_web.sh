#!/bin/bash
# Script pour démarrer l'interface web Flask de la serre

echo "🌐 Démarrage de l'interface web Flask - Serre Connectée"
echo "=========================================================="

# Répertoire du projet
PROJECT_DIR="/home/ulysse/Projet_IoT_RaspberryPi"
cd "$PROJECT_DIR" || exit 1

# Arrêter tous les processus Python existants (sans confirmation)
if pgrep -f "python.*app.py" > /dev/null || pgrep -f "python.*main.py" > /dev/null; then
    echo "🛑 Arrêt des processus Python existants..."
    pkill -f "python.*app.py" 2>/dev/null
    pkill -f "python.*main.py" 2>/dev/null
    sleep 2
    echo "✅ Processus arrêtés"
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
echo "🚀 Démarrage de Flask..."
echo ""

# Démarrer Flask
python src/api/app.py &
FLASK_PID=$!

# Attendre que Flask démarre
sleep 3

# Vérifier que Flask tourne
if ps -p $FLASK_PID > /dev/null 2>&1; then
    echo "=========================================================="
    echo "✅ Flask démarré avec succès !"
    echo ""
    echo "📱 Accès à l'interface web :"
    echo "   - Local:   http://localhost:5000"
    echo "   - Réseau:  http://$LOCAL_IP:5000"
    echo ""
    echo "🛑 Pour arrêter Flask :"
    echo "   pkill -f 'python src/api/app.py'"
    echo "   ou: kill $FLASK_PID"
    echo ""
    echo "📋 Logs en temps réel :"
    echo "   tail -f data/logs/serre_controller.log"
    echo "=========================================================="
else
    echo "❌ Échec du démarrage de Flask"
    echo "Vérifiez les logs dans data/logs/serre_controller.log"
    exit 1
fi
