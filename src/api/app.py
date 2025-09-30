# src/api/api.py
"""
API REST FastAPI - Serre Connectée
Remplace Flask pour standardiser l'architecture
"""
import sys
import os
import threading
import logging
import signal
import time
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

try:
    from src.core.orchestrator import SerreOrchestrator
    from src import config
except ImportError as e:
    print(f"Erreur d'importation critique: {e}")
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
    description="API REST pour le contrôle et monitoring de la serre",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS pour permettre les requêtes depuis Electron/mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale du contrôleur
controller: Optional[SerreOrchestrator] = None
controller_thread: Optional[threading.Thread] = None
shutdown_event = threading.Event()


# Modèles Pydantic
class ActuatorControl(BaseModel):
    active: bool
    state: Optional[bool] = False


class SettingsUpdate(BaseModel):
    settings: dict


# Événement de démarrage
@app.on_event("startup")
async def startup_event():
    """Initialise le contrôleur au démarrage de l'API"""
    global controller, controller_thread
    
    logger.info("Démarrage de l'API FastAPI...")
    logger.info(f"Mode matériel: {config.HARDWARE_ENV}")
    logger.info(f"Type BD: {config.DB_TYPE}")
    
    try:
        controller = SerreOrchestrator()
        logger.info("SerreOrchestrator initialisé")
        
        # Démarrer le contrôleur dans un thread
        controller_thread = threading.Thread(
            target=controller.run,
            name="OrchestrateurThread",
            daemon=True
        )
        controller_thread.start()
        logger.info("Thread du contrôleur démarré")
        
    except Exception as e:
        logger.critical(f"Échec de l'initialisation du contrôleur: {e}", exc_info=True)
        raise


# Événement d'arrêt
@app.on_event("shutdown")
async def shutdown_event():
    """Arrêt propre du contrôleur"""
    global controller
    
    logger.info("Arrêt de l'API...")
    if controller:
        controller.shutdown()
    logger.info("API arrêtée")


# Routes
@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "name": "Serre Connectée API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "status": "/api/status",
            "settings": "/api/settings",
            "control": "/api/control/{device}",
            "docs": "/docs"
        }
    }


@app.get("/api/status")
async def get_status():
    """Récupère l'état complet du système"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        return controller.get_status()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """Récupère tous les paramètres de configuration"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        return controller.get_all_settings()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paramètres: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/settings")
async def update_settings(update: SettingsUpdate):
    """Met à jour les paramètres de configuration"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        success = controller.update_settings(update.settings)
        if success:
            return {
                "success": True,
                "message": "Paramètres mis à jour",
                "settings": controller.get_all_settings()
            }
        else:
            raise HTTPException(status_code=400, detail="Échec de la mise à jour")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/leds")
async def control_leds(control: ActuatorControl):
    """Contrôle manuel des LEDs"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        controller.set_leds_manual_mode(control.active, control.state)
        return {
            "success": True,
            "device": "leds",
            "manual_mode": control.active,
            "state": control.state
        }
    except Exception as e:
        logger.error(f"Erreur contrôle LEDs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/humidifier")
async def control_humidifier(control: ActuatorControl):
    """Contrôle manuel de l'humidificateur"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        controller.set_humidifier_manual_mode(control.active, control.state)
        return {
            "success": True,
            "device": "humidifier",
            "manual_mode": control.active,
            "state": control.state
        }
    except Exception as e:
        logger.error(f"Erreur contrôle humidificateur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/ventilation")
async def control_ventilation(control: ActuatorControl):
    """Contrôle manuel de la ventilation"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        controller.set_ventilation_manual_mode(control.active, control.state)
        return {
            "success": True,
            "device": "ventilation",
            "manual_mode": control.active,
            "state": control.state
        }
    except Exception as e:
        logger.error(f"Erreur contrôle ventilation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/auto")
async def set_auto_mode():
    """Remet tous les actionneurs en mode automatique"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        controller.set_all_auto_mode()
        return {
            "success": True,
            "message": "Mode automatique activé pour tous les actionneurs"
        }
    except Exception as e:
        logger.error(f"Erreur mode auto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/emergency_stop")
async def emergency_stop():
    """Arrêt d'urgence - désactive tous les actionneurs"""
    if not controller:
        raise HTTPException(status_code=503, detail="Contrôleur non initialisé")
    
    try:
        controller.emergency_stop_all_actuators()
        return {
            "success": True,
            "message": "Arrêt d'urgence effectué"
        }
    except Exception as e:
        logger.error(f"Erreur arrêt d'urgence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check pour monitoring"""
    return {
        "status": "healthy" if controller else "degraded",
        "version": "2.0.0"
    }


# Point d'entrée
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Démarrage de l'API FastAPI sur {config.APP_HOST}:{config.APP_PORT}")
    
    # Gérer les signaux d'arrêt
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt...")
        shutdown_event.set()
        if controller:
            controller.shutdown()
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
        if controller:
            controller.shutdown()
