#!/bin/bash
# Script pour arrêter tous les processus de la serre

echo "🛑 Arrêt de tous les processus - Serre Connectée"
echo "=================================================="

# Arrêter l'API de monitoring
if pgrep -f "python src/api/monitoring_api.py" > /dev/null; then
    echo "Arrêt de l'API de monitoring..."
    pkill -f "python src/api/monitoring_api.py"
    sleep 1
    echo "✅ API arrêtée"
else
    echo "ℹ️  L'API de monitoring n'était pas en cours d'exécution"
fi

# Arrêter main.py
if pgrep -f "python main.py" > /dev/null; then
    echo "Arrêt de main.py..."
    pkill -f "python main.py"
    sleep 1
    echo "✅ main.py arrêté"
else
    echo "ℹ️  main.py n'était pas en cours d'exécution"
fi

# Arrêter le service systemd s'il existe
if systemctl is-active --quiet serre.service 2>/dev/null; then
    echo "Arrêt du service systemd..."
    sudo systemctl stop serre.service
    echo "✅ Service arrêté"
fi

echo ""
echo "✅ Tous les processus ont été arrêtés"
echo "=================================================="
