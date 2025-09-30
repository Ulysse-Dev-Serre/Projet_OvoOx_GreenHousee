# src/core/services/actuator_coordinator.py
"""
Service de coordination des actionneurs
Responsabilité unique : Coordonner les actionneurs en fonction des données capteurs
"""
import logging
import threading
from typing import Dict, Any
from src.core.services.sensor_service import SensorData
from src.core.services.configuration_manager import ConfigurationManager


class ActuatorCoordinator:
    """
    Service responsable de la coordination des actionneurs
    
    Principe SRP : Une seule responsabilité = Coordonner les actionneurs
    - Reçoit les données des capteurs
    - Met à jour l'état des actionneurs
    - Gère les modes manuel/automatique
    """
    
    def __init__(
        self,
        led_controller,
        humidifier_controller,
        ventilation_controller,
        config_manager: ConfigurationManager
    ):
        """
        Args:
            led_controller: Contrôleur des LEDs
            humidifier_controller: Contrôleur de l'humidificateur
            ventilation_controller: Contrôleur de la ventilation
            config_manager: Gestionnaire de configuration
        """
        self.logger = logging.getLogger(__name__)
        
        self.led_ctrl = led_controller
        self.humidifier_ctrl = humidifier_controller
        self.ventilation_ctrl = ventilation_controller
        self.config_manager = config_manager
        
        # Verrou pour sérialiser les commandes de contrôle manuel
        self._control_lock = threading.Lock()
        
        self.logger.info("ActuatorCoordinator initialisé")
    
    def update_from_sensor_data(self, sensor_data: SensorData):
        """
        Met à jour les actionneurs en fonction des données capteurs
        
        Args:
            sensor_data: Données des capteurs
        """
        if not sensor_data.is_valid:
            self.logger.debug("Données capteurs invalides, pas de mise à jour")
            return
        
        # Préparer les données pour les contrôleurs
        current_data = {
            'temperature': sensor_data.temperature,
            'humidite': sensor_data.humidity,
            'co2': sensor_data.co2
        }
        
        # Mettre à jour chaque actionneur
        try:
            self.led_ctrl.update_state(current_data)
            self.humidifier_ctrl.update_state(current_data)
            self.ventilation_ctrl.update_state(current_data)
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des actionneurs: {e}")
    
    def get_all_status(self) -> Dict[str, Any]:
        """
        Récupère l'état de tous les actionneurs
        
        Returns:
            Dictionnaire avec l'état de chaque actionneur
        """
        return {
            "leds": self.led_ctrl.get_status(),
            "humidifier": self.humidifier_ctrl.get_status(),
            "ventilation": self.ventilation_ctrl.get_status()
        }
    
    def set_led_manual_mode(self, active: bool, state_if_manual: bool = False):
        """Active/désactive le mode manuel pour les LEDs (thread-safe)"""
        with self._control_lock:
            self.led_ctrl.set_manual_mode(active, state_if_manual)
            self.logger.info(
                f"LEDs: mode manuel {'activé' if active else 'désactivé'}"
                + (f" (état: {state_if_manual})" if active else "")
            )
            self._force_update(self.led_ctrl)
    
    def set_humidifier_manual_mode(self, active: bool, state_if_manual: bool = False):
        """Active/désactive le mode manuel pour l'humidificateur (thread-safe)"""
        with self._control_lock:
            self.humidifier_ctrl.set_manual_mode(active, state_if_manual)
            self.logger.info(
                f"Humidificateur: mode manuel {'activé' if active else 'désactivé'}"
                + (f" (état: {state_if_manual})" if active else "")
            )
            self._force_update(self.humidifier_ctrl)
    
    def set_ventilation_manual_mode(self, active: bool, state_if_manual: bool = False):
        """Active/désactive le mode manuel pour la ventilation (thread-safe)"""
        with self._control_lock:
            self.ventilation_ctrl.set_manual_mode(active, state_if_manual)
            self.logger.info(
                f"Ventilation: mode manuel {'activé' if active else 'désactivé'}"
                + (f" (état: {state_if_manual})" if active else "")
            )
            self._force_update(self.ventilation_ctrl)
    
    def set_all_auto_mode(self):
        """Remet tous les actionneurs en mode automatique (thread-safe)"""
        with self._control_lock:
            self.led_ctrl.set_manual_mode(False)
            self.humidifier_ctrl.set_manual_mode(False)
            self.ventilation_ctrl.set_manual_mode(False)
            
            # Forcer une mise à jour immédiate
            self._force_update(self.led_ctrl)
            self._force_update(self.humidifier_ctrl)
            self._force_update(self.ventilation_ctrl)
            
            self.logger.info("Tous les actionneurs sont en mode automatique")
    
    def emergency_stop_all(self):
        """Arrêt d'urgence : désactive tous les actionneurs (thread-safe)"""
        with self._control_lock:
            self.logger.warning("ARRÊT D'URGENCE ACTIVÉ")
            
            self.led_ctrl.set_manual_mode(True, False)
            self.humidifier_ctrl.set_manual_mode(True, False)
            self.ventilation_ctrl.set_manual_mode(True, False)
            
            self._force_update(self.led_ctrl)
            self._force_update(self.humidifier_ctrl)
            self._force_update(self.ventilation_ctrl)
            
            self.logger.info("Tous les actionneurs désactivés (arrêt d'urgence)")
    
    def _force_update(self, actuator_controller):
        """Force une mise à jour immédiate d'un actionneur"""
        # Obtenir les dernières données capteurs (ou valeurs par défaut)
        dummy_data = {'temperature': None, 'humidite': None, 'co2': None}
        actuator_controller.update_state(dummy_data)
        actuator_controller._control_hardware()
