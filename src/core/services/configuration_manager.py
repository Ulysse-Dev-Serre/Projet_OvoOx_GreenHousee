# src/core/services/configuration_manager.py
"""
Service de gestion de la configuration
Responsabilité unique : Charger, sauvegarder et fournir les paramètres de configuration
"""
import json
import os
import threading
import logging
from typing import Dict, Any, Optional
from src import config


class ConfigurationManager:
    """
    Service responsable de la gestion de la configuration
    
    Principe SRP : Une seule responsabilité = Gérer la configuration
    - Charge les paramètres depuis user_settings.json
    - Sauvegarde les modifications
    - Fournit un accès thread-safe aux paramètres
    - Fusionne avec les valeurs par défaut
    """
    
    def __init__(self, settings_file: Optional[str] = None):
        """
        Args:
            settings_file: Chemin vers le fichier de configuration
                          (défaut: config.USER_SETTINGS_FILE)
        """
        self.logger = logging.getLogger(__name__)
        self.settings_file = settings_file or config.USER_SETTINGS_FILE
        
        # Stockage des paramètres
        self._settings: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Charger les paramètres au démarrage
        self.load_settings()
    
    def load_settings(self) -> bool:
        """
        Charge les paramètres depuis le fichier
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        # S'assurer que le répertoire existe
        if not self._ensure_directory_exists():
            self.logger.warning("Impossible de créer le répertoire des paramètres")
            with self._lock:
                self._settings = config.DEFAULT_SETTINGS.copy()
            return False
        
        # Commencer avec les valeurs par défaut
        loaded_settings = config.DEFAULT_SETTINGS.copy()
        
        try:
            # Charger depuis le fichier s'il existe
            if os.path.exists(self.settings_file) and os.path.getsize(self.settings_file) > 0:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    
                    # Fusionner avec les valeurs par défaut
                    for key, value in user_settings.items():
                        if key in loaded_settings:
                            # Conversion de type si nécessaire
                            default_type = type(loaded_settings[key])
                            try:
                                loaded_settings[key] = self._cast_value(
                                    value, default_type
                                )
                            except (ValueError, TypeError) as e:
                                self.logger.warning(
                                    f"Erreur de conversion pour '{key}': {e}. "
                                    f"Utilisation de la valeur par défaut"
                                )
                        else:
                            self.logger.warning(f"Clé inconnue '{key}' ignorée")
                    
                    self.logger.info(f"Paramètres chargés depuis '{self.settings_file}'")
            else:
                # Fichier n'existe pas, le créer avec les valeurs par défaut
                self.logger.info(
                    f"Fichier de paramètres non trouvé. "
                    f"Création de '{self.settings_file}' avec valeurs par défaut"
                )
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(loaded_settings, f, indent=4, ensure_ascii=False)
        
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(
                f"Erreur lors du chargement de '{self.settings_file}': {e}. "
                f"Utilisation des valeurs par défaut"
            )
            loaded_settings = config.DEFAULT_SETTINGS.copy()
        
        # Stocker les paramètres
        with self._lock:
            self._settings = loaded_settings
        
        self.logger.info(f"Paramètres actifs: {self._settings}")
        return True
    
    def save_settings(self) -> bool:
        """
        Sauvegarde les paramètres dans le fichier
        
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        if not self._ensure_directory_exists():
            self.logger.error("Impossible de sauvegarder, répertoire inaccessible")
            return False
        
        with self._lock:
            settings_to_save = self._settings.copy()
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Paramètres sauvegardés dans '{self.settings_file}'")
            return True
        
        except IOError as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère un paramètre
        
        Args:
            key: Clé du paramètre
            default: Valeur par défaut si non trouvée
        
        Returns:
            Valeur du paramètre ou default
        """
        with self._lock:
            # Chercher dans les paramètres chargés
            if key in self._settings:
                return self._settings[key]
        
        # Chercher dans les valeurs par défaut
        if key in config.DEFAULT_SETTINGS:
            return config.DEFAULT_SETTINGS[key]
        
        # Utiliser la valeur par défaut fournie
        if default is not None:
            return default
        
        self.logger.warning(
            f"Paramètre '{key}' non trouvé et aucune valeur par défaut fournie"
        )
        return None
    
    def get_all(self) -> Dict[str, Any]:
        """
        Récupère tous les paramètres (fusionnés avec les défauts)
        
        Returns:
            Dictionnaire complet des paramètres
        """
        with self._lock:
            complete_settings = config.DEFAULT_SETTINGS.copy()
            complete_settings.update(self._settings)
            return complete_settings
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Met à jour un ou plusieurs paramètres
        
        Args:
            updates: Dictionnaire des paramètres à mettre à jour
        
        Returns:
            True si au moins un paramètre a été modifié et sauvegardé
        """
        if not isinstance(updates, dict):
            self.logger.error("Les mises à jour doivent être un dictionnaire")
            return False
        
        self.logger.info(f"Mise à jour des paramètres: {updates}")
        
        changes_made = False
        
        with self._lock:
            temp_settings = self._settings.copy()
            
            for key, new_value in updates.items():
                # Vérifier que la clé est valide
                if key not in config.DEFAULT_SETTINGS:
                    self.logger.warning(f"Clé inconnue '{key}' ignorée")
                    continue
                
                # Obtenir le type attendu
                default_value = config.DEFAULT_SETTINGS[key]
                expected_type = type(default_value)
                
                # Convertir si nécessaire
                try:
                    casted_value = self._cast_value(new_value, expected_type)
                    
                    # Vérifier si la valeur a vraiment changé
                    old_value = temp_settings.get(key)
                    if old_value != casted_value:
                        temp_settings[key] = casted_value
                        changes_made = True
                        self.logger.info(
                            f"Paramètre '{key}' modifié: {old_value} → {casted_value}"
                        )
                    else:
                        self.logger.debug(f"Paramètre '{key}' inchangé")
                
                except (ValueError, TypeError) as e:
                    self.logger.warning(
                        f"Impossible de convertir '{key}' = '{new_value}' "
                        f"en {expected_type}: {e}"
                    )
            
            # Appliquer les changements
            if changes_made:
                self._settings = temp_settings
        
        # Sauvegarder si des changements ont été faits
        if changes_made:
            return self.save_settings()
        
        return not changes_made  # True si aucun changement (pas d'erreur)
    
    def _ensure_directory_exists(self) -> bool:
        """S'assure que le répertoire du fichier de configuration existe"""
        directory = os.path.dirname(self.settings_file)
        
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"Répertoire créé: {directory}")
                return True
            except OSError as e:
                self.logger.error(f"Impossible de créer le répertoire '{directory}': {e}")
                return False
        
        return True
    
    @staticmethod
    def _cast_value(value: Any, target_type: type) -> Any:
        """
        Convertit une valeur vers le type cible
        
        Args:
            value: Valeur à convertir
            target_type: Type cible
        
        Returns:
            Valeur convertie
        
        Raises:
            ValueError, TypeError: Si la conversion échoue
        """
        # Gestion spéciale pour les booléens
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ['true', 'on', '1', 'yes', 'vrai']
            elif isinstance(value, (int, float)):
                return bool(value)
            else:
                return bool(value)
        
        # Gestion spéciale pour les entiers (accepter les flottants)
        if target_type == int and isinstance(value, (float, str)):
            return int(float(value))
        
        # Conversion standard
        return target_type(value)
