# src/core/services/sensor_service.py
"""
Service d'acquisition des données capteurs
Responsabilité unique : Lire les capteurs et notifier les observateurs
"""
import threading
import time
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Callable


@dataclass
class SensorData:
    """Structure de données pour les lectures de capteurs"""
    timestamp: float
    temperature: Optional[float]
    humidity: Optional[float]
    co2: Optional[float]
    is_valid: bool
    
    @classmethod
    def create_invalid(cls):
        """Crée une instance de données invalides"""
        return cls(
            timestamp=time.time(),
            temperature=None,
            humidity=None,
            co2=None,
            is_valid=False
        )


class SensorAcquisitionService:
    """
    Service responsable de l'acquisition des données capteurs
    
    Principe SRP : Une seule responsabilité = Lire les capteurs
    - Gère la boucle d'acquisition dans un thread
    - Stocke la dernière lecture valide
    - Notifie les observateurs lors de nouvelles données
    """
    
    def __init__(self, hardware_interface, interval_seconds: int = 15):
        """
        Args:
            hardware_interface: Interface matérielle pour lire les capteurs
            interval_seconds: Intervalle entre chaque lecture
        """
        self.logger = logging.getLogger(__name__)
        self.hardware = hardware_interface
        self.interval = interval_seconds
        
        # État des données
        self._latest_data: SensorData = SensorData.create_invalid()
        self._data_lock = threading.Lock()
        self._last_error_logged = False
        
        # Événements de contrôle
        self._running = threading.Event()
        self._first_valid_data_event = threading.Event()
        
        # Observateurs (callbacks)
        self._observers: List[Callable[[SensorData], None]] = []
        
        # Thread d'acquisition
        self._thread: Optional[threading.Thread] = None
    
    def subscribe(self, observer: Callable[[SensorData], None]):
        """Ajoute un observateur qui sera notifié à chaque nouvelle lecture"""
        self._observers.append(observer)
        self.logger.debug(f"Observateur ajouté. Total: {len(self._observers)}")
    
    def start(self):
        """Démarre le service d'acquisition"""
        if self._thread and self._thread.is_alive():
            self.logger.warning("Service déjà démarré")
            return
        
        self._running.set()
        self._thread = threading.Thread(
            target=self._acquisition_loop,
            name="SensorAcquisitionService",
            daemon=True
        )
        self._thread.start()
        self.logger.info(f"Service d'acquisition démarré (intervalle: {self.interval}s)")
    
    def stop(self, timeout: float = 10.0):
        """Arrête le service d'acquisition"""
        if not self._thread or not self._thread.is_alive():
            self.logger.info("Service déjà arrêté")
            return
        
        self.logger.info("Arrêt du service d'acquisition...")
        self._running.clear()
        self._thread.join(timeout=timeout)
        
        if self._thread.is_alive():
            self.logger.warning("Le thread n'a pas pu être arrêté dans le délai imparti")
        else:
            self.logger.info("Service d'acquisition arrêté")
    
    def get_latest_data(self) -> SensorData:
        """Retourne la dernière lecture de capteurs"""
        with self._data_lock:
            return SensorData(
                timestamp=self._latest_data.timestamp,
                temperature=self._latest_data.temperature,
                humidity=self._latest_data.humidity,
                co2=self._latest_data.co2,
                is_valid=self._latest_data.is_valid
            )
    
    def wait_for_first_valid_data(self, timeout: float = 90.0) -> bool:
        """
        Attend la première lecture valide
        
        Returns:
            True si des données valides ont été reçues, False sinon
        """
        self.logger.info(f"Attente de la première lecture valide (max {timeout}s)...")
        result = self._first_valid_data_event.wait(timeout=timeout)
        
        if result:
            self.logger.info("Première lecture valide reçue")
        else:
            self.logger.warning("Délai d'attente dépassé pour la première lecture valide")
        
        return result
    
    def _acquisition_loop(self):
        """Boucle principale d'acquisition des capteurs"""
        self.logger.info(f"Boucle d'acquisition active (intervalle: {self.interval}s)")
        
        while self._running.is_set():
            loop_start_time = time.time()
            
            try:
                # Lire les capteurs
                temp, hum, co2_val = self.hardware.lire_capteur()
                
                # Créer l'objet de données
                if temp is not None and hum is not None and co2_val is not None:
                    sensor_data = SensorData(
                        timestamp=time.time(),
                        temperature=temp,
                        humidity=hum,
                        co2=co2_val,
                        is_valid=True
                    )
                    
                    # Stocker les données
                    with self._data_lock:
                        self._latest_data = sensor_data
                    
                    # Notifier la première lecture valide
                    if not self._first_valid_data_event.is_set():
                        self._first_valid_data_event.set()
                        self.logger.info("Première lecture valide des capteurs obtenue")
                    
                    # Réinitialiser le flag d'erreur
                    if self._last_error_logged:
                        self.logger.info("Lecture des capteurs réussie après erreur")
                        self._last_error_logged = False
                    
                    # Notifier les observateurs
                    self._notify_observers(sensor_data)
                    
                    self.logger.debug(
                        f"Capteurs: T={temp:.1f}°C, H={hum:.1f}%, CO2={co2_val:.0f}ppm"
                    )
                else:
                    # Données invalides
                    with self._data_lock:
                        self._latest_data.is_valid = False
                    
                    if not self._last_error_logged:
                        self.logger.warning(
                            f"Données invalides: T={temp}, H={hum}, CO2={co2_val}"
                        )
                        self._last_error_logged = True
            
            except Exception as e:
                with self._data_lock:
                    self._latest_data.is_valid = False
                
                self.logger.error(f"Erreur lors de l'acquisition: {e}", exc_info=True)
                self._last_error_logged = True
            
            # Attente avant la prochaine lecture
            elapsed_time = time.time() - loop_start_time
            wait_time = self.interval - elapsed_time
            
            if wait_time > 0:
                self._sleep_interruptible(wait_time)
        
        self.logger.info("Boucle d'acquisition terminée")
    
    def _sleep_interruptible(self, duration: float, chunk: float = 0.5):
        """Sommeil interruptible pour arrêt rapide"""
        slept = 0.0
        while slept < duration and self._running.is_set():
            time_to_sleep = min(chunk, duration - slept)
            time.sleep(time_to_sleep)
            slept += time_to_sleep
    
    def _notify_observers(self, data: SensorData):
        """Notifie tous les observateurs des nouvelles données"""
        for observer in self._observers:
            try:
                observer(data)
            except Exception as e:
                self.logger.error(f"Erreur lors de la notification d'un observateur: {e}")
