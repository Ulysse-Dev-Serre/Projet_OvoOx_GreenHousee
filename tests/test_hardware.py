#!/usr/bin/env python3
"""
Script de test du matériel - Serre Connectée
Vérifie que le capteur SCD30 et les GPIO fonctionnent correctement
"""

import sys
import os
import time

# Ajouter le répertoire du projet au path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

os.environ['HARDWARE_ENV'] = 'raspberry_pi'
os.environ['DB_TYPE'] = 'sqlite'

from src.hardware_interface.raspberry_pi import RaspberryPiHardware

def test_sensor():
    """Test du capteur SCD30"""
    print("\n" + "="*60)
    print("Test du capteur SCD30")
    print("="*60)
    
    try:
        hardware = RaspberryPiHardware()
        print("✅ Matériel initialisé avec succès")
        
        print("\nLecture de 5 échantillons (1 par seconde)...")
        for i in range(5):
            temp, hum, co2 = hardware.lire_capteur()
            if temp is not None:
                print(f"  {i+1}. Température: {temp:.1f}°C | Humidité: {hum:.1f}% | CO2: {co2:.0f}ppm")
            else:
                print(f"  {i+1}. ❌ Échec de lecture")
            time.sleep(1)
        
        print("\n✅ Test du capteur terminé")
        
        # Test rapide des GPIO
        print("\n" + "="*60)
        print("Test des actionneurs (GPIO)")
        print("="*60)
        
        print("\n1. Test des LEDs...")
        hardware.activer_leds()
        print("   LEDs activées pendant 2 secondes")
        time.sleep(2)
        hardware.desactiver_leds()
        print("   LEDs désactivées")
        
        print("\n2. Test de la ventilation...")
        hardware.activer_ventilation()
        print("   Ventilation activée pendant 2 secondes")
        time.sleep(2)
        hardware.desactiver_ventilation()
        print("   Ventilation désactivée")
        
        print("\n3. Test de l'humidificateur...")
        hardware.activer_humidificateur()
        print("   Humidificateur activé pendant 2 secondes")
        time.sleep(2)
        hardware.desactiver_humidificateur()
        print("   Humidificateur désactivé")
        
        print("\n✅ Test des actionneurs terminé")
        
        # Nettoyage
        hardware.cleanup()
        print("\n✅ Nettoyage effectué")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🔧 Script de test du matériel - Serre Connectée")
    print("⚠️  Ce script va activer/désactiver les actionneurs pendant quelques secondes")
    print("   Assurez-vous que c'est sans danger pour votre installation")
    
    input("\nAppuyez sur Enter pour continuer ou Ctrl+C pour annuler...")
    
    success = test_sensor()
    
    print("\n" + "="*60)
    if success:
        print("✅ TOUS LES TESTS RÉUSSIS")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
