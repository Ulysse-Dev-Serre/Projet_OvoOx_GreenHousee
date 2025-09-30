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
from src.core.actuators.actuator_registry import ActuatorRegistry


class ActuatorCoordinator:
    """
    Service responsable de la coordination des actionneurs
    
    Principe SRP : Une seule responsabilité = Coordonner les actionneurs
    Principe OCP : Ouvert à l'extension (nouveaux actionneurs), fermé à la modification
    - Reçoit les données des capteurs
    - Met à jour l'état des actionneurs via le registre
    - Gère les modes manuel/automatique
    """
    
    def __init__(self, config_manager: ConfigurationManager, sensor_service):
        """
        Args:
            config_manager: Gestionnaire de configuration
            sensor_service: Service d'acquisition des capteurs
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.sensor_service = sensor_service
        
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
        
        # Mettre à jour tous les actionneurs du registre
        try:
            for name, actuator in ActuatorRegistry.get_all().items():
                actuator.update_state(current_data)
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des actionneurs: {e}")
    
    def get_all_status(self) -> Dict[str, Any]:
        """
        Récupère l'état de tous les actionneurs
        
        Returns:
            Dictionnaire avec l'état de chaque actionneur
        """
        status = {}
        for name, actuator in ActuatorRegistry.get_all().items():
            status[name] = actuator.get_status()
        return status
    
    def set_actuator_manual_mode(self, actuator_name: str, active: bool, state_if_manual: bool = False):
        """Active/désactive le mode manuel pour un actionneur spécifique (thread-safe)"""
        with self._control_lock:
            try:
                actuator = ActuatorRegistry.get(actuator_name)
                actuator.set_manual_mode(active, state_if_manual)
                self.logger.info(
                    f"{actuator_name}: mode manuel {'activé' if active else 'désactivé'}"
                    + (f" (état: {state_if_manual})" if active else "")
                )
                self._force_update(actuator)
            except KeyError:
                self.logger.error(f"Actionneur '{actuator_name}' non trouvé dans le registre")
    
    def set_all_auto_mode(self):
        """Remet tous les actionneurs en mode automatique (thread-safe)"""
        with self._control_lock:
            for name, actuator in ActuatorRegistry.get_all().items():
                actuator.set_manual_mode(False)
                self._force_update(actuator)
            
            self.logger.info("Tous les actionneurs sont en mode automatique")
    
    def emergency_stop_all(self):
        """Arrêt d'urgence : désactive tous les actionneurs (thread-safe)"""
        with self._control_lock:
            self.logger.warning("ARRÊT D'URGENCE ACTIVÉ")
            
            for name, actuator in ActuatorRegistry.get_all().items():
                actuator.set_manual_mode(True, False)
                self._force_update(actuator)
            
            self.logger.info("Tous les actionneurs désactivés (arrêt d'urgence)")
    
    def _force_update(self, actuator_controller):
        """Force une mise à jour immédiate d'un actionneur"""
        # Obtenir les dernières données capteurs réelles
        latest_data = self.sensor_service.get_latest_data()
        current_data = {
            'temperature': latest_data.temperature,
            'humidite': latest_data.humidity,
            'co2': latest_data.co2
        }
        actuator_controller.update_state(current_data)
        actuator_controller._control_hardware()
