# src/core/actuators/actuator_registry.py
"""
Registry pattern pour la gestion dynamique des actionneurs
Permet d'ajouter de nouveaux actionneurs sans modifier le code existant (Open/Closed Principle)
"""
import logging
from typing import Dict, List, Type, Any
from src.core.actuators.base_actuator import BaseActuator


class ActuatorRegistry:
    """
    Registre central pour tous les actionneurs du système
    
    Principe OCP : Ouvert à l'extension (ajout de nouveaux actionneurs),
                   Fermé à la modification (pas besoin de modifier ce code)
    """
    
    _instance = None
    _actuators: Dict[str, BaseActuator] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ActuatorRegistry, cls).__new__(cls)
            cls._instance._actuators = {}
        return cls._instance
    
    @classmethod
    def register(cls, name: str, actuator: BaseActuator):
        """
        Enregistre un nouvel actionneur dans le registre
        
        Args:
            name: Nom unique de l'actionneur (ex: 'leds', 'humidifier')
            actuator: Instance de l'actionneur
        """
        if not cls._instance:
            cls()
        
        if name in cls._instance._actuators:
            logging.warning(f"Actuator '{name}' already registered, overwriting")
        
        cls._instance._actuators[name] = actuator
        logging.info(f"Actuator '{name}' registered successfully")
    
    @classmethod
    def unregister(cls, name: str):
        """
        Désenregistre un actionneur
        
        Args:
            name: Nom de l'actionneur à désenregistrer
        """
        if cls._instance and name in cls._instance._actuators:
            del cls._instance._actuators[name]
            logging.info(f"Actuator '{name}' unregistered")
    
    @classmethod
    def get(cls, name: str) -> BaseActuator:
        """
        Récupère un actionneur par son nom
        
        Args:
            name: Nom de l'actionneur
            
        Returns:
            L'instance de l'actionneur
            
        Raises:
            KeyError: Si l'actionneur n'existe pas
        """
        if not cls._instance:
            raise KeyError(f"No actuators registered yet")
        
        if name not in cls._instance._actuators:
            raise KeyError(f"Actuator '{name}' not found in registry")
        
        return cls._instance._actuators[name]
    
    @classmethod
    def get_all(cls) -> Dict[str, BaseActuator]:
        """
        Récupère tous les actionneurs enregistrés
        
        Returns:
            Dictionnaire {nom: actuator}
        """
        if not cls._instance:
            return {}
        return cls._instance._actuators.copy()
    
    @classmethod
    def get_all_names(cls) -> List[str]:
        """
        Récupère les noms de tous les actionneurs enregistrés
        
        Returns:
            Liste des noms d'actionneurs
        """
        if not cls._instance:
            return []
        return list(cls._instance._actuators.keys())
    
    @classmethod
    def clear(cls):
        """Vide le registre (utile pour les tests)"""
        if cls._instance:
            cls._instance._actuators.clear()
            logging.info("Actuator registry cleared")
