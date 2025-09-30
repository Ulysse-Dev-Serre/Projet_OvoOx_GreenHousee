# src/core/services/data_persistence_service.py
"""
Service de persistance des données
Responsabilité unique : Sauvegarder les données dans la base de données
"""
import logging
from datetime import datetime
from typing import Optional
from src.core.services.sensor_service import SensorData


class DataPersistenceService:
    """
    Service responsable de la persistence des données
    
    Principe SRP : Une seule responsabilité = Sauvegarder les données
    - Reçoit les données des capteurs et actionneurs
    - Les envoie au gestionnaire de base de données
    - Gère le buffer et le flush
    """
    
    def __init__(self, db_manager):
        """
        Args:
            db_manager: Gestionnaire de base de données (DatabaseManager ou SQLiteDatabaseManager)
        """
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.logger.info("DataPersistenceService initialisé")
    
    def save_sensor_data(
        self,
        sensor_data: SensorData,
        actuators_status: dict
    ):
        """
        Sauvegarde les données des capteurs et l'état des actionneurs
        
        Args:
            sensor_data: Données des capteurs
            actuators_status: État des actionneurs (dict avec keys: leds, humidifier, ventilation)
        """
        if not sensor_data.is_valid:
            self.logger.debug("Données capteurs invalides, pas de sauvegarde")
            return
        
        try:
            # Extraire les états des actionneurs
            leds_status = actuators_status.get("leds", {})
            humid_status = actuators_status.get("humidifier", {})
            vent_status = actuators_status.get("ventilation", {})
            
            # Appeler le gestionnaire de base de données
            self.db_manager.add_sensor_data_to_buffer(
                timestamp=datetime.fromtimestamp(sensor_data.timestamp).replace(microsecond=0),
                temperature=sensor_data.temperature,
                humidity=sensor_data.humidity,
                co2=sensor_data.co2,
                humidifier_active=humid_status.get("is_active", False),
                ventilation_active=vent_status.get("is_active", False),
                leds_active=leds_status.get("is_active", False),
                humidifier_on_duration=humid_status.get("on_duration_seconds") if humid_status.get("is_active") else None,
                humidifier_off_duration=humid_status.get("off_duration_seconds") if not humid_status.get("is_active") else None,
                ventilation_on_duration=vent_status.get("on_duration_seconds") if vent_status.get("is_active") else None,
                ventilation_off_duration=vent_status.get("off_duration_seconds") if not vent_status.get("is_active") else None
            )
            
            self.logger.debug("Données ajoutées au buffer de la base de données")
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des données: {e}", exc_info=True)
    
    def flush(self):
        """Force le vidage du buffer vers la base de données"""
        try:
            self.db_manager.flush_buffer()
            self.logger.debug("Buffer de la base de données vidé")
        except Exception as e:
            self.logger.error(f"Erreur lors du flush: {e}")
    
    def close(self):
        """Ferme la connexion à la base de données"""
        try:
            self.logger.info("Fermeture de la base de données...")
            self.db_manager.flush_buffer()
            self.db_manager.close_pool()
            self.logger.info("Base de données fermée")
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de la BD: {e}")
