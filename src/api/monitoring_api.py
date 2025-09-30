# src/api/monitoring_api.py
"""
API REST FastAPI - Serre Connectée (Mode Contrôle Actif)
API unifiée pour monitoring ET contrôle via injection de l'orchestrateur
"""
import sys
import os
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from src import config
except ImportError as e:
    print(f"Erreur d'importation critique: {e}")
    sys.exit(1)

# Import du gestionnaire SQLite
try:
    if config.DB_TYPE == 'sqlite':
        from src.utils.db_utils_sqlite import SQLiteDatabaseManager
        logging.info("API avec SQLite pour lecture des données")
    else:
        from src.utils.db_utils_sqlite import SQLiteDatabaseManager
        logging.warning("Fallback sur SQLite pour la lecture")
except ImportError as e:
    print(f"Erreur d'importation: {e}")
    sys.exit(1)

# Configuration du logging
log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Serre Connectée API",
    description="API REST complète pour monitoring et contrôle de la serre",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS sécurisée pour Electron
# Autorise les origines locales et file:// pour les apps Electron
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["*"],  # TODO: Retirer "*" en production
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Instances globales
db_manager: Optional[SQLiteDatabaseManager] = None
orchestrator_instance = None  # Injecté depuis main.py

# Clé API pour authentification simple
API_KEY = os.getenv("API_KEY", "dev-key-change-in-production")


# Modèles Pydantic
class ActuatorControl(BaseModel):
    """Contrôle d'un actionneur"""
    manual_mode: bool = Field(..., description="True pour mode manuel, False pour mode auto")
    state: Optional[bool] = Field(None, description="État ON/OFF si en mode manuel")


class SettingsUpdate(BaseModel):
    """Mise à jour des paramètres de configuration"""
    settings: dict = Field(..., description="Dictionnaire des paramètres à mettre à jour")


# Fonction d'authentification
async def verify_api_key(x_api_key: str = Header(None)):
    """Vérifie la clé API dans le header X-API-Key"""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante"
        )
    return True


# Fonction pour injecter l'orchestrateur
def attach_orchestrator(orchestrator):
    """
    Injecte l'instance de l'orchestrateur dans l'API
    À appeler depuis main.py après l'initialisation
    """
    global orchestrator_instance
    orchestrator_instance = orchestrator
    logger.info("✅ Orchestrateur injecté dans l'API - Endpoints de contrôle activés")


def get_orchestrator():
    """Dependency pour obtenir l'orchestrateur"""
    if orchestrator_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrateur non disponible. L'API n'est pas complètement initialisée."
        )
    return orchestrator_instance


# Événement de démarrage
@app.on_event("startup")
async def startup_event():
    """Initialise la connexion SQLite"""
    global db_manager
    
    logger.info("Démarrage de l'API FastAPI...")
    logger.info(f"Type BD: {config.DB_TYPE}")
    logger.info(f"Clé API: {API_KEY[:8]}... (configurée via env API_KEY)")
    
    try:
        db_manager = SQLiteDatabaseManager()
        logger.info("✅ Connexion SQLite établie")
    except Exception as e:
        logger.critical(f"❌ Échec de la connexion SQLite: {e}", exc_info=True)
        raise


# Événement d'arrêt
@app.on_event("shutdown")
async def shutdown_event():
    """Fermeture propre de la connexion SQLite"""
    global db_manager
    
    logger.info("Arrêt de l'API...")
    if db_manager:
        try:
            db_manager.close_pool()
            logger.info("Connexion SQLite fermée")
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")


# Routes
@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "name": "Serre Connectée API",
        "version": "3.0.0",
        "status": "running",
        "mode": "full-control" if orchestrator_instance else "read-only",
        "authentication": "Requis (X-API-Key header) pour les endpoints de contrôle",
        "endpoints": {
            "status": "/api/status",
            "settings": "/api/settings",
            "history": "/api/history",
            "control": "/api/control/*",
            "docs": "/docs"
        }
    }


@app.get("/api/status")
async def get_status():
    """Récupère l'état complet du système depuis SQLite"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Base de données non disponible")
    
    try:
        # Lire la dernière entrée de la base de données
        import sqlite3
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, temperature, humidity, co2,
                   leds_active, humidifier_active, ventilation_active
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Aucune donnée disponible")
        
        # Si l'orchestrateur est disponible, obtenir le status complet avec durées
        if orchestrator_instance:
            status = orchestrator_instance.get_status()
            return {
                "timestamp": status.get("timestamp"),
                "temperature": status.get("temperature"),
                "humidite": status.get("humidite"),
                "co2": status.get("co2"),
                "sensor_read_ok": status.get("sensor_read_ok", True),
                "leds": status.get("leds", {}),
                "humidifier": status.get("humidifier", {}),
                "ventilation": status.get("ventilation", {})
            }
        
        # Sinon, lire depuis la base (sans durées ni modes)
        return {
            "timestamp": row[0],
            "temperature": row[1],
            "humidite": row[2],
            "co2": row[3],
            "sensor_read_ok": True,
            "leds": {
                "is_active": bool(row[4]),
                "manual_mode": False
            },
            "humidifier": {
                "is_active": bool(row[5]),
                "manual_mode": False
            },
            "ventilation": {
                "is_active": bool(row[6]),
                "manual_mode": False
            }
        }
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du statut: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """Récupère les paramètres de configuration"""
    try:
        # Si l'orchestrateur est disponible, obtenir les settings via le ConfigurationManager
        if orchestrator_instance:
            all_settings = orchestrator_instance.get_all_settings()
            return all_settings
        
        # Sinon, utiliser les valeurs par défaut de config.py
        return {
            "HEURE_DEBUT_LEDS": config.HEURE_DEBUT_LEDS,
            "HEURE_FIN_LEDS": config.HEURE_FIN_LEDS,
            "SEUIL_HUMIDITE_ON": config.SEUIL_HUMIDITE_ON,
            "SEUIL_HUMIDITE_OFF": config.SEUIL_HUMIDITE_OFF,
            "SEUIL_CO2_MAX": config.SEUIL_CO2_MAX,
            "HEURE_DEBUT_JOUR_OPERATION": config.HEURE_DEBUT_JOUR_OPERATION,
            "HEURE_FIN_JOUR_OPERATION": config.HEURE_FIN_JOUR_OPERATION
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paramètres: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history(limit: int = 100):
    """Récupère l'historique des données"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Base de données non disponible")
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, temperature, humidity, co2,
                   leds_active, humidifier_active, ventilation_active
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "count": len(rows),
            "data": [
                {
                    "timestamp": row[0],
                    "temperature": row[1],
                    "humidity": row[2],
                    "co2": row[3],
                    "leds_active": bool(row[4]),
                    "humidifier_active": bool(row[5]),
                    "ventilation_active": bool(row[6])
                }
                for row in rows
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de l'historique: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints de contrôle (Authentification requise)
@app.put("/api/settings", dependencies=[Depends(verify_api_key)])
async def update_settings(
    update: SettingsUpdate,
    orchestrator = Depends(get_orchestrator)
):
    """
    Met à jour les paramètres de configuration
    Requiert: X-API-Key header
    """
    try:
        success = orchestrator.update_settings(update.settings)
        if success:
            return {
                "success": True,
                "message": "Paramètres mis à jour avec succès",
                "new_settings": orchestrator.get_all_settings()
            }
        else:
            raise HTTPException(status_code=400, detail="Échec de la mise à jour")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des paramètres: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/leds", dependencies=[Depends(verify_api_key)])
async def control_leds(
    control: ActuatorControl,
    orchestrator = Depends(get_orchestrator)
):
    """
    Contrôle manuel des LEDs
    Requiert: X-API-Key header
    """
    try:
        orchestrator.set_leds_manual_mode(
            active=control.manual_mode,
            state_if_manual=control.state if control.state is not None else False
        )
        return {
            "success": True,
            "actuator": "leds",
            "manual_mode": control.manual_mode,
            "state": control.state
        }
    except Exception as e:
        logger.error(f"Erreur contrôle LEDs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/humidifier", dependencies=[Depends(verify_api_key)])
async def control_humidifier(
    control: ActuatorControl,
    orchestrator = Depends(get_orchestrator)
):
    """
    Contrôle manuel de l'humidificateur
    Requiert: X-API-Key header
    """
    try:
        orchestrator.set_humidifier_manual_mode(
            active=control.manual_mode,
            state_if_manual=control.state if control.state is not None else False
        )
        return {
            "success": True,
            "actuator": "humidifier",
            "manual_mode": control.manual_mode,
            "state": control.state
        }
    except Exception as e:
        logger.error(f"Erreur contrôle humidificateur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/ventilation", dependencies=[Depends(verify_api_key)])
async def control_ventilation(
    control: ActuatorControl,
    orchestrator = Depends(get_orchestrator)
):
    """
    Contrôle manuel de la ventilation
    Requiert: X-API-Key header
    """
    try:
        orchestrator.set_ventilation_manual_mode(
            active=control.manual_mode,
            state_if_manual=control.state if control.state is not None else False
        )
        return {
            "success": True,
            "actuator": "ventilation",
            "manual_mode": control.manual_mode,
            "state": control.state
        }
    except Exception as e:
        logger.error(f"Erreur contrôle ventilation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/auto", dependencies=[Depends(verify_api_key)])
async def set_auto_mode(orchestrator = Depends(get_orchestrator)):
    """
    Remet tous les actionneurs en mode automatique
    Requiert: X-API-Key header
    """
    try:
        orchestrator.set_all_auto_mode()
        return {
            "success": True,
            "message": "Tous les actionneurs sont en mode automatique",
            "status": orchestrator.get_status()
        }
    except Exception as e:
        logger.error(f"Erreur passage mode auto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/emergency_stop", dependencies=[Depends(verify_api_key)])
async def emergency_stop(orchestrator = Depends(get_orchestrator)):
    """
    Arrêt d'urgence - Désactive tous les actionneurs
    Requiert: X-API-Key header
    """
    try:
        orchestrator.emergency_stop_all_actuators()
        return {
            "success": True,
            "message": "ARRÊT D'URGENCE ACTIVÉ - Tous les actionneurs désactivés",
            "status": orchestrator.get_status()
        }
    except Exception as e:
        logger.error(f"Erreur arrêt d'urgence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check pour monitoring"""
    return {
        "status": "healthy" if db_manager else "degraded",
        "version": "3.0.0",
        "mode": "full-control" if orchestrator_instance else "read-only",
        "orchestrator": "attached" if orchestrator_instance else "not attached"
    }


# Fonction pour démarrer l'API dans un thread (appelée depuis main.py)
def start_api_server():
    """Démarre le serveur FastAPI (utilisé par main.py)"""
    import uvicorn
    
    logger.info(f"🚀 Démarrage de l'API FastAPI sur {config.APP_HOST}:{config.APP_PORT}")
    if orchestrator_instance:
        logger.info("✅ Mode: Full Control (orchestrateur attaché)")
    else:
        logger.warning("⚠️ Mode: Read-Only (orchestrateur non attaché)")
    
    uvicorn.run(
        app,
        host=config.APP_HOST,
        port=config.APP_PORT,
        log_level="info"
    )


# Point d'entrée standalone (si lancé directement - déprécié)
if __name__ == "__main__":
    import uvicorn
    
    logger.warning("⚠️ DÉPRÉCIÉ: Lancer 'python main.py' à la place pour avoir le contrôle complet")
    logger.info(f"Démarrage de l'API FastAPI sur {config.APP_HOST}:{config.APP_PORT}")
    logger.warning("Mode READ-ONLY car aucun orchestrateur n'est injecté")
    
    # Gérer les signaux d'arrêt
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt...")
        if db_manager:
            db_manager.close_pool()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        uvicorn.run(
            app,
            host=config.APP_HOST,
            port=config.APP_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Arrêt par Ctrl+C")
        if db_manager:
            db_manager.close_pool()
