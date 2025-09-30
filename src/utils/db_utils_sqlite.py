# src/utils/db_utils_sqlite.py
import sqlite3
import logging
import time
from datetime import datetime
from pathlib import Path

try:
    from src.config import BUFFER_SIZE_MAX, FLUSH_INTERVAL_BUFFER_SECONDES, PROJECT_ROOT_DIR
except ImportError:
    logging.critical("CRITICAL (db_utils_sqlite.py): config.py non trouvé! Utilisation de valeurs par défaut.")
    BUFFER_SIZE_MAX = 10
    FLUSH_INTERVAL_BUFFER_SECONDES = 300
    PROJECT_ROOT_DIR = "/home/ulysse/Projet_IoT_RaspberryPi"

db_logger = logging.getLogger("db_utils_sqlite")

class SQLiteDatabaseManager:
    """Gestionnaire de base de données SQLite pour la serre"""
    
    def __init__(self, db_path: str = None):
        """
        Initialise la connexion SQLite
        
        Args:
            db_path: Chemin vers le fichier SQLite (défaut: data/serre.db)
        """
        if db_path is None:
            db_path = str(Path(PROJECT_ROOT_DIR) / "data" / "serre.db")
        
        self.db_path = db_path
        self.data_buffer = []
        self.last_flush_time = time.time()
        
        # Créer le répertoire si nécessaire
        db_dir = Path(db_path).parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            db_logger.info(f"Répertoire créé : {db_dir}")
        
        # Initialiser la base de données
        self._initialize_database()
        db_logger.info(f"Base de données SQLite initialisée : {self.db_path}")
    
    def _initialize_database(self):
        """Crée la table sensor_data si elle n'existe pas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Créer la table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL,
                    humidity REAL,
                    co2 REAL,
                    humidifier_active BOOLEAN,
                    ventilation_active BOOLEAN,
                    leds_active BOOLEAN,
                    humidifier_on_duration_seconds REAL,
                    humidifier_off_duration_seconds REAL,
                    ventilation_on_duration_seconds REAL,
                    ventilation_off_duration_seconds REAL
                )
            ''')
            
            # Créer des index pour améliorer les performances
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON sensor_data(timestamp DESC)
            ''')
            
            conn.commit()
            conn.close()
            
            db_logger.info("Table sensor_data et index créés avec succès")
            self._test_connection()
            
        except sqlite3.Error as e:
            db_logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            raise
    
    def _test_connection(self):
        """Test de connexion à la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            count = cursor.fetchone()[0]
            conn.close()
            db_logger.info(f"Connexion à la base de données réussie. {count} enregistrements existants.")
        except sqlite3.Error as e:
            db_logger.error(f"Échec du test de connexion: {e}")
    
    def add_sensor_data_to_buffer(self, timestamp: datetime, temperature: float | None, humidity: float | None, 
                                  co2: float | None, humidifier_active: bool, ventilation_active: bool, 
                                  leds_active: bool, humidifier_on_duration: float | None, 
                                  humidifier_off_duration: float | None, ventilation_on_duration: float | None, 
                                  ventilation_off_duration: float | None):
        """Ajoute des données au buffer avant insertion dans la BD"""
        
        record = (
            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            round(temperature, 1) if temperature is not None else None,
            round(humidity, 1) if humidity is not None else None,
            round(co2, 0) if co2 is not None else None,
            humidifier_active,
            ventilation_active,
            leds_active,
            round(humidifier_on_duration, 1) if humidifier_on_duration is not None else None,
            round(humidifier_off_duration, 1) if humidifier_off_duration is not None else None,
            round(ventilation_on_duration, 1) if ventilation_on_duration is not None else None,
            round(ventilation_off_duration, 1) if ventilation_off_duration is not None else None
        )
        
        self.data_buffer.append(record)
        db_logger.debug(f"Donnée ajoutée au buffer. Taille: {len(self.data_buffer)}")
        
        current_time = time.time()
        
        # Flush si buffer plein ou intervalle dépassé
        if len(self.data_buffer) >= BUFFER_SIZE_MAX or \
           (current_time - self.last_flush_time) >= FLUSH_INTERVAL_BUFFER_SECONDES:
            self.flush_buffer()
    
    def flush_buffer(self):
        """Vide le buffer dans la base de données"""
        if not self.data_buffer:
            return
        
        buffer_to_flush = list(self.data_buffer)
        db_logger.info(f"Tentative d'insertion de {len(buffer_to_flush)} enregistrements")
        
        max_retries = 2
        attempt = 0
        
        while attempt <= max_retries:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                sql_insert_query = '''
                    INSERT INTO sensor_data (
                        timestamp, temperature, humidity, co2,
                        humidifier_active, ventilation_active, leds_active,
                        humidifier_on_duration_seconds, humidifier_off_duration_seconds,
                        ventilation_on_duration_seconds, ventilation_off_duration_seconds
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                cursor.executemany(sql_insert_query, buffer_to_flush)
                conn.commit()
                conn.close()
                
                db_logger.info(f"{len(buffer_to_flush)} enregistrements insérés avec succès")
                self.data_buffer.clear()
                self.last_flush_time = time.time()
                return
                
            except sqlite3.Error as e:
                db_logger.error(f"Erreur DB lors de l'insertion (tentative {attempt + 1}/{max_retries + 1}): {e}")
                attempt += 1
                
                if attempt <= max_retries:
                    sleep_time = 2 ** attempt
                    db_logger.info(f"Nouvel essai dans {sleep_time} secondes...")
                    time.sleep(sleep_time)
                else:
                    db_logger.critical(f"Échec définitif après {max_retries + 1} tentatives")
                    return
                    
            except Exception as e:
                db_logger.critical(f"Erreur inattendue: {e}", exc_info=True)
                return
    
    def close_pool(self):
        """Ferme la connexion et vide le buffer final"""
        db_logger.info("Vidage final du buffer avant fermeture...")
        self.flush_buffer()
        db_logger.info("Base de données SQLite fermée")
    
    def get_latest_readings(self, limit: int = 10):
        """Récupère les dernières lectures (pour debug/test)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, temperature, humidity, co2, 
                       leds_active, humidifier_active, ventilation_active
                FROM sensor_data
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except sqlite3.Error as e:
            db_logger.error(f"Erreur lors de la lecture des données: {e}")
            return []
