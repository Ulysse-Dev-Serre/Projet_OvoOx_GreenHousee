#!/usr/bin/env python3
"""
Test de la refactorisation SRP
Vérifie que le nouvel orchestrateur fonctionne correctement
"""
import sys
import os
import time

# Ajouter le répertoire du projet au path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

os.environ['HARDWARE_ENV'] = 'mock'
os.environ['DB_TYPE'] = 'sqlite'

from src.core.orchestrator import SerreOrchestrator

def test_orchestrator():
    print("\n" + "="*60)
    print("Test du nouvel orchestrateur (SRP Refactoring)")
    print("="*60)
    
    try:
        # Créer l'orchestrateur
        print("\n1. Création de l'orchestrateur...")
        orchestrator = SerreOrchestrator()
        print("✅ Orchestrateur créé avec succès")
        
        # Attendre quelques secondes pour avoir des données
        print("\n2. Attente de données capteurs (3 secondes)...")
        time.sleep(3)
        
        # Récupérer le statut
        print("\n3. Récupération du statut...")
        status = orchestrator.get_status()
        print(f"✅ Statut récupéré:")
        print(f"   - Température: {status['temperature']}°C")
        print(f"   - Humidité: {status['humidite']}%")
        print(f"   - CO2: {status['co2']}ppm")
        print(f"   - Capteurs OK: {status['sensor_read_ok']}")
        print(f"   - LEDs actives: {status['leds']['is_active']}")
        print(f"   - Humidificateur actif: {status['humidifier']['is_active']}")
        print(f"   - Ventilation active: {status['ventilation']['is_active']}")
        
        # Tester la récupération de configuration
        print("\n4. Test de récupération de configuration...")
        settings = orchestrator.get_all_settings()
        print(f"✅ {len(settings)} paramètres configurés")
        print(f"   - Heure début LEDs: {settings.get('HEURE_DEBUT_LEDS', 'N/A')}")
        print(f"   - Seuil humidité ON: {settings.get('SEUIL_HUMIDITE_ON', 'N/A')}%")
        print(f"   - Seuil CO2 max: {settings.get('SEUIL_CO2_MAX', 'N/A')}ppm")
        
        # Tester la mise à jour de configuration
        print("\n5. Test de mise à jour de configuration...")
        result = orchestrator.update_settings({"HEURE_DEBUT_LEDS": 9})
        print(f"✅ Mise à jour: {'réussie' if result else 'échouée'}")
        new_value = orchestrator.get_all_settings()["HEURE_DEBUT_LEDS"]
        print(f"   - Nouvelle valeur: {new_value}")
        
        # Tester le contrôle manuel
        print("\n6. Test du contrôle manuel...")
        orchestrator.set_leds_manual_mode(True, True)
        time.sleep(1)
        status = orchestrator.get_status()
        print(f"✅ Mode manuel LEDs: {status['leds']['manual_mode']}")
        print(f"   - État: {status['leds']['is_active']}")
        
        # Remettre en auto
        orchestrator.set_all_auto_mode()
        print("✅ Retour en mode automatique")
        
        # Arrêt propre
        print("\n7. Arrêt de l'orchestrateur...")
        orchestrator.shutdown()
        print("✅ Orchestrateur arrêté proprement")
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS RÉUSSIS")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_orchestrator()
    sys.exit(0 if success else 1)
