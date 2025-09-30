# src/core/orchestrator.py
"""
Orchestrateur principal de la serre
Responsabilité unique : Coordonner les différents services
"""
import logging
import time
import importlib
from src import config

# Import des services
from src.core.services.sensor_service import SensorAcquisitionService, SensorData
from src.core.services.configuration_manager import ConfigurationManager
from src.core.services.actuator_coordinator import ActuatorCoordinator
from src.core.services.data_persistence_service import DataPersistenceService

# Import des contrôleurs d'actionneurs
from src.core.actuators.led_controller import LedController
from src.core.actuators.humidifier_controller import HumidifierController
from src.core.actuators.ventilation_controller import VentilationController

# Import du gestionnaire de base de données
try:
    if config.DB_TYPE == 'sqlite':
        from src.utils.db_utils_sqlite import SQLiteDatabaseManager as DatabaseManager
        logging.info("Utilisation de SQLite pour la base de données")
    else:
        from src.utils.db_utils import DatabaseManager
        logging.info("Utilisation de PostgreSQL pour la base de données")
except ImportError as e:
    logging.warning(f"DatabaseManager non trouvé: {e}. Utilisation de MockDatabaseManager.")
    class MockDatabaseManager:
        def __init__(self, *args, **kwargs): pass
        def add_sensor_data_to_buffer(self, *args, **kwargs): logging.debug("MockDM: add_sensor_data_to_buffer")
        def flush_buffer(self): logging.debug("MockDM: flush_buffer")
        def close_pool(self): logging.debug("MockDM: close_pool")
    DatabaseManager = MockDatabaseManager


class SerreOrchestrator:
    """
    Orchestrateur principal de la serre
    
    Principe SRP : Une seule responsabilité = Coordonner les services
    - Initialise tous les services
    - Gère le cycle de vie de l'application
    - Coordonne la communication entre services
    
    N'a PLUS les responsabilités suivantes (déléguées aux services) :
    - Lecture des capteurs → SensorAcquisitionService
    - Gestion de la configuration → ConfigurationManager
    - Coordination des actionneurs → ActuatorCoordinator
    - Persistence des données → DataPersistenceService
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de SerreOrchestrator...")
        
        # Initialisation du matériel
        self.hardware = self._initialize_hardware()
        
        # Initialisation des services
        self.config_manager = ConfigurationManager()
        self.db_manager = self._initialize_db_manager()
        
        # Créer les contrôleurs d'actionneurs
        self.led_ctrl = LedController(self.hardware, self.config_manager)
        self.humidifier_ctrl = HumidifierController(self.hardware, self.config_manager)
        self.ventilation_ctrl = VentilationController(self.hardware, self.config_manager)
        
        # Créer les services métier
        self.sensor_service = SensorAcquisitionService(
            hardware_interface=self.hardware,
            interval_seconds=config.INTERVALLE_LECTURE_RAPIDE_CAPTEURS_SECONDES
        )
        
        self.actuator_coordinator = ActuatorCoordinator(
            led_controller=self.led_ctrl,
            humidifier_controller=self.humidifier_ctrl,
            ventilation_controller=self.ventilation_ctrl,
            config_manager=self.config_manager
        )
        
        self.data_persistence = DataPersistenceService(
            db_manager=self.db_manager
        )
        
        # S'abonner aux événements des capteurs
        self.sensor_service.subscribe(self._on_sensor_data)
        
        # Démarrer le service d'acquisition
        self.sensor_service.start()
        
        # Attendre la première lecture valide
        self.sensor_service.wait_for_first_valid_data(
            timeout=config.INTERVALLE_LECTURE_RAPIDE_CAPTEURS_SECONDES * 6
        )
        
        self.logger.info("SerreOrchestrator initialisé avec succès")
    
    def _initialize_hardware(self):
        """Charge dynamiquement l'interface matérielle"""
        hardware_interface_module_path = 'src.hardware_interface'
        hardware_env = getattr(config, 'HARDWARE_ENV', 'mock')
        
        if hardware_env == 'raspberry_pi':
            try:
                module_path = f'{hardware_interface_module_path}.raspberry_pi'
                hw_module = importlib.import_module(module_path)
                HardwareInterface = hw_module.RaspberryPiHardware
                self.logger.info("Utilisation de RaspberryPiHardware")
            except ImportError as e:
                self.logger.error(f"Erreur importation RaspberryPiHardware: {e}. Fallback sur MockHardware")
                module_path = f'{hardware_interface_module_path}.mock_hardware'
                hw_module = importlib.import_module(module_path)
                HardwareInterface = hw_module.MockHardware
        else:
            module_path = f'{hardware_interface_module_path}.mock_hardware'
            hw_module = importlib.import_module(module_path)
            HardwareInterface = hw_module.MockHardware
            self.logger.info(f"Utilisation de MockHardware")
        
        return HardwareInterface()
    
    def _initialize_db_manager(self):
        """Initialise le gestionnaire de base de données"""
        try:
            if hasattr(config, 'ACTIVE_DB_CONFIG') and config.ACTIVE_DB_CONFIG:
                return DatabaseManager()
            else:
                self.logger.warning("Config BD non trouvée. Utilisation de MockDatabaseManager")
                return MockDatabaseManager()
        except Exception as e:
            self.logger.error(f"Erreur initialisation BD: {e}. Utilisation de MockDatabaseManager")
            return MockDatabaseManager()
    
    def _on_sensor_data(self, sensor_data: SensorData):
        """
        Callback appelé lors de nouvelles données capteurs
        
        Args:
            sensor_data: Nouvelles données des capteurs
        """
        # Mettre à jour les actionneurs
        self.actuator_coordinator.update_from_sensor_data(sensor_data)
        
        # Sauvegarder les données
        actuators_status = self.actuator_coordinator.get_all_status()
        self.data_persistence.save_sensor_data(sensor_data, actuators_status)
    
    def get_status(self) -> dict:
        """Retourne l'état complet du système"""
        sensor_data = self.sensor_service.get_latest_data()
        actuators_status = self.actuator_coordinator.get_all_status()
        
        return {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "temperature": f"{sensor_data.temperature:.1f}" if sensor_data.temperature is not None else "N/A",
            "humidite": f"{sensor_data.humidity:.1f}" if sensor_data.humidity is not None else "N/A",
            "co2": f"{sensor_data.co2:.0f}" if sensor_data.co2 is not None else "N/A",
            "sensor_read_ok": sensor_data.is_valid,
            **actuators_status
        }
    
    def get_all_settings(self) -> dict:
        """Retourne tous les paramètres de configuration"""
        return self.config_manager.get_all()
    
    def update_settings(self, new_settings: dict) -> bool:
        """Met à jour les paramètres de configuration"""
        return self.config_manager.update(new_settings)
    
    # Méthodes de contrôle manuel (délégation)
    def set_leds_manual_mode(self, active: bool, state_if_manual: bool = False):
        self.actuator_coordinator.set_led_manual_mode(active, state_if_manual)
    
    def set_humidifier_manual_mode(self, active: bool, state_if_manual: bool = False):
        self.actuator_coordinator.set_humidifier_manual_mode(active, state_if_manual)
    
    def set_ventilation_manual_mode(self, active: bool, state_if_manual: bool = False):
        self.actuator_coordinator.set_ventilation_manual_mode(active, state_if_manual)
    
    def set_all_auto_mode(self):
        self.actuator_coordinator.set_all_auto_mode()
    
    def emergency_stop_all_actuators(self):
        self.actuator_coordinator.emergency_stop_all()
    
    def run(self):
        """Boucle principale (bloquante)"""
        self.logger.info("SerreOrchestrator.run() - Boucle principale active")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt reçu, arrêt...")
            self.shutdown()
    
    def shutdown(self):
        """Arrêt propre de tous les services"""
        self.logger.info("Arrêt de SerreOrchestrator...")
        
        # Arrêter le service de capteurs
        self.sensor_service.stop()
        
        # Vider et fermer la base de données
        self.data_persistence.close()
        
        # Nettoyer le matériel
        if self.hardware:
            self.logger.info("Nettoyage du matériel...")
            self.hardware.cleanup()
        
        self.logger.info("SerreOrchestrator arrêté")
