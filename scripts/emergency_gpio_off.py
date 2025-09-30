#!/usr/bin/env python3
"""
Script d'urgence pour éteindre tous les GPIO
Usage: python scripts/emergency_gpio_off.py
"""

try:
    import lgpio
    
    # GPIO à éteindre (mettre à 1 = OFF pour relais)
    GPIOS = [27, 26, 13, 22]  # LEDs, Fan humid, Brumisateur, Ventilation
    
    print("🚨 Arrêt d'urgence des GPIO...")
    
    # Ouvrir le chip GPIO
    h = lgpio.gpiochip_open(0)
    print(f"✓ GPIO chip ouvert (handle: {h})")
    
    # Éteindre chaque GPIO
    for gpio in GPIOS:
        lgpio.gpio_claim_output(h, gpio)
        lgpio.gpio_write(h, gpio, 1)  # 1 = OFF (logique inverse)
        print(f"✓ GPIO {gpio} → OFF")
    
    # Fermer le chip
    lgpio.gpiochip_close(h)
    print("\n✅ Tous les actionneurs sont éteints")
    print("✅ GPIO chip fermé proprement")
    
except ImportError:
    print("❌ Erreur: lgpio n'est pas installé")
    print("Installation: pip install lgpio")
except Exception as e:
    print(f"❌ Erreur: {e}")
