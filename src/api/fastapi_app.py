# src/api/fastapi_app.py
"""
API REST FastAPI pour application mobile/desktop
Ne touche PAS aux GPIO - Lit uniquement la base de données SQLite
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
import os
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "serre.db"

app = FastAPI(
    title="Serre Connectée API",
    description="API REST pour l'application mobile de gestion de serre",
    version="2.0.0"
)

# CORS pour permettre les requêtes depuis l'application mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    """Obtient une connexion à la base SQLite"""
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Base de données non trouvée")
    return sqlite3.connect(str(DB_PATH))


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Serre Connectée API",
        "version": "2.0.0",
        "endpoints": {
            "status": "/api/v1/status",
            "history": "/api/v1/sensors/history",
            "latest": "/api/v1/sensors/latest",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.get("/api/v1/status")
async def get_status():
    """
    Récupère l'état actuel du système (dernière lecture)
    """
    try:
        conn = get_db_connection()
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
        
        return {
            "timestamp": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "co2": row[3],
            "actuators": {
                "leds": {"active": bool(row[4])},
                "humidifier": {"active": bool(row[5])},
                "ventilation": {"active": bool(row[6])}
            }
        }
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données: {e}")


@app.get("/api/v1/sensors/latest")
async def get_latest_sensor_data():
    """Récupère la dernière lecture des capteurs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, temperature, humidity, co2
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Aucune donnée disponible")
        
        return {
            "timestamp": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "co2": row[3]
        }
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données: {e}")


@app.get("/api/v1/sensors/history")
async def get_sensor_history(
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'enregistrements"),
    offset: int = Query(0, ge=0, description="Décalage pour pagination"),
    start_date: Optional[str] = Query(None, description="Date de début (ISO format)"),
    end_date: Optional[str] = Query(None, description="Date de fin (ISO format)")
):
    """
    Récupère l'historique des capteurs avec pagination
    
    Exemple: /api/v1/sensors/history?limit=50&offset=0
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construire la requête avec filtres optionnels
        query = "SELECT timestamp, temperature, humidity, co2 FROM sensor_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Compter le total pour la pagination
        count_query = "SELECT COUNT(*) FROM sensor_data WHERE 1=1"
        count_params = []
        if start_date:
            count_query += " AND timestamp >= ?"
            count_params.append(start_date)
        if end_date:
            count_query += " AND timestamp <= ?"
            count_params.append(end_date)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "data": [
                {
                    "timestamp": row[0],
                    "temperature": row[1],
                    "humidity": row[2],
                    "co2": row[3]
                }
                for row in rows
            ],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "returned": len(rows)
            }
        }
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données: {e}")


@app.get("/api/v1/statistics/daily")
async def get_daily_statistics(
    days: int = Query(7, ge=1, le=90, description="Nombre de jours")
):
    """Statistiques quotidiennes agrégées"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(humidity) as avg_humidity,
                MIN(humidity) as min_humidity,
                MAX(humidity) as max_humidity,
                AVG(co2) as avg_co2,
                MIN(co2) as min_co2,
                MAX(co2) as max_co2,
                COUNT(*) as count
            FROM sensor_data
            WHERE timestamp >= DATE('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "period_days": days,
            "statistics": [
                {
                    "date": row[0],
                    "temperature": {
                        "avg": round(row[1], 1) if row[1] else None,
                        "min": round(row[2], 1) if row[2] else None,
                        "max": round(row[3], 1) if row[3] else None
                    },
                    "humidity": {
                        "avg": round(row[4], 1) if row[4] else None,
                        "min": round(row[5], 1) if row[5] else None,
                        "max": round(row[6], 1) if row[6] else None
                    },
                    "co2": {
                        "avg": round(row[7], 0) if row[7] else None,
                        "min": round(row[8], 0) if row[8] else None,
                        "max": round(row[9], 0) if row[9] else None
                    },
                    "reading_count": row[10]
                }
                for row in rows
            ]
        }
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données: {e}")


@app.get("/health")
async def health_check():
    """Health check pour monitoring"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_records": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
