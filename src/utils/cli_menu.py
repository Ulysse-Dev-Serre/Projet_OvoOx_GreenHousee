# src/utils/cli_menu.py
"""
Menu CLI interactif pour contrôler la serre
S'exécute dans un thread séparé pour permettre l'interaction pendant que la serre fonctionne
"""
import logging
import threading


class CLIMenu:
    """Menu interactif en ligne de commande"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)
        self._running = True
    
    def start(self):
        """Démarre le menu dans un thread"""
        menu_thread = threading.Thread(
            target=self._menu_loop,
            name="CLIMenuThread",
            daemon=True
        )
        menu_thread.start()
        self.logger.info("Menu CLI démarré")
    
    def _menu_loop(self):
        """Boucle principale du menu"""
        while self._running:
            try:
                self._display_menu()
                choice = input("\n→ Choix : ").strip()
                self._handle_choice(choice)
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Erreur dans le menu: {e}")
    
    def _display_menu(self):
        """Affiche le menu"""
        status = self.orchestrator.get_status()
        
        print("\n" + "="*60)
        print("🌱 SERRE CONNECTÉE - Menu de contrôle")
        print("="*60)
        print(f"\n📊 État actuel ({status['timestamp']}):")
        print(f"   🌡️  Température  : {status['temperature']}°C")
        print(f"   💧 Humidité     : {status['humidite']}%")
        print(f"   🌫️  CO2          : {status['co2']} ppm")
        print(f"\n💡 Actionneurs :")
        
        leds = status['leds']
        print(f"   LEDs          : {'🟢 ON' if leds['is_active'] else '🔴 OFF'} "
              f"({'MANUEL' if leds['manual_mode'] else 'AUTO'})")
        
        humid = status['humidifier']
        print(f"   Humidificateur: {'🟢 ON' if humid['is_active'] else '🔴 OFF'} "
              f"({'MANUEL' if humid['manual_mode'] else 'AUTO'})")
        
        vent = status['ventilation']
        print(f"   Ventilation   : {'🟢 ON' if vent['is_active'] else '🔴 OFF'} "
              f"({'MANUEL' if vent['manual_mode'] else 'AUTO'})")
        
        print("\n" + "-"*60)
        print("Commandes disponibles :")
        print("  1) Activer LEDs (manuel)")
        print("  2) Désactiver LEDs (manuel)")
        print("  3) Activer Humidificateur (manuel)")
        print("  4) Désactiver Humidificateur (manuel)")
        print("  5) Activer Ventilation (manuel)")
        print("  6) Désactiver Ventilation (manuel)")
        print("  7) Mode AUTO pour tous")
        print("  8) Arrêt d'urgence (tout OFF)")
        print("  9) Afficher configuration")
        print("  0) Rafraîchir")
        print("  q) Quitter")
        print("-"*60)
    
    def _handle_choice(self, choice):
        """Traite le choix de l'utilisateur"""
        try:
            if choice == '1':
                self.orchestrator.set_leds_manual_mode(True, True)
                print("✅ LEDs activées en mode manuel")
            
            elif choice == '2':
                self.orchestrator.set_leds_manual_mode(True, False)
                print("✅ LEDs désactivées en mode manuel")
            
            elif choice == '3':
                self.orchestrator.set_humidifier_manual_mode(True, True)
                print("✅ Humidificateur activé en mode manuel")
            
            elif choice == '4':
                self.orchestrator.set_humidifier_manual_mode(True, False)
                print("✅ Humidificateur désactivé en mode manuel")
            
            elif choice == '5':
                self.orchestrator.set_ventilation_manual_mode(True, True)
                print("✅ Ventilation activée en mode manuel")
            
            elif choice == '6':
                self.orchestrator.set_ventilation_manual_mode(True, False)
                print("✅ Ventilation désactivée en mode manuel")
            
            elif choice == '7':
                self.orchestrator.set_all_auto_mode()
                print("✅ Mode automatique activé pour tous les actionneurs")
            
            elif choice == '8':
                confirm = input("⚠️  Confirmer l'arrêt d'urgence ? (o/N) : ")
                if confirm.lower() == 'o':
                    self.orchestrator.emergency_stop_all_actuators()
                    print("🚨 Arrêt d'urgence effectué - Tous les actionneurs désactivés")
                else:
                    print("❌ Arrêt d'urgence annulé")
            
            elif choice == '9':
                self._display_settings()
            
            elif choice == '0':
                pass  # Rafraîchir - juste réafficher le menu
            
            elif choice.lower() == 'q':
                print("\n👋 Au revoir !")
                self._running = False
            
            else:
                print("❌ Choix invalide")
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
            self.logger.error(f"Erreur lors du traitement du choix '{choice}': {e}")
    
    def _display_settings(self):
        """Affiche la configuration"""
        settings = self.orchestrator.get_all_settings()
        
        print("\n" + "="*60)
        print("⚙️  Configuration actuelle")
        print("="*60)
        print(f"  Horaires LEDs        : {settings['HEURE_DEBUT_LEDS']}h - {settings['HEURE_FIN_LEDS']}h")
        print(f"  Seuil humidité ON    : {settings['SEUIL_HUMIDITE_ON']}%")
        print(f"  Seuil humidité OFF   : {settings['SEUIL_HUMIDITE_OFF']}%")
        print(f"  Seuil CO2 max        : {settings['SEUIL_CO2_MAX']} ppm")
        print(f"  Horaires opération   : {settings['HEURE_DEBUT_JOUR_OPERATION']}h - {settings['HEURE_FIN_JOUR_OPERATION']}h")
        print("="*60)
        
        input("\nAppuyez sur Enter pour continuer...")
