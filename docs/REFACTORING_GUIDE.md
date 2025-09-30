# Guide de Refactorisation - Projet Serre Connectée

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Analyse de l'architecture actuelle](#analyse-de-larchitecture-actuelle)
3. [Principes SOLID et Design Patterns](#principes-solid-et-design-patterns)
4. [Plan de refactorisation](#plan-de-refactorisation)
5. [Optimisation de la base de données](#optimisation-de-la-base-de-données)
6. [API REST pour intégration mobile](#api-rest-pour-intégration-mobile)
7. [Roadmap d'implémentation](#roadmap-dimplémentation)

---

## 🎯 Vue d'ensemble

### Objectifs de la refactorisation

1. **Améliorer la maintenabilité** : Application des principes SOLID
2. **Augmenter la flexibilité** : Utilisation de design patterns appropriés
3. **Préparer l'intégration mobile** : API REST complète pour Flutter
4. **Optimiser la base de données** : Structure adaptée aux besoins mobiles et analytiques

### Architecture actuelle

```
src/
├── api/                    # Flask API et interface web
│   ├── app.py             # Routes et logique API
│   └── templates/
├── core/                   # Logique métier
│   ├── serre_logic.py     # Contrôleur principal (SerreController)
│   └── actuators/         # Contrôleurs d'actionneurs
│       ├── base_actuator.py
│       ├── led_controller.py
│       ├── humidifier_controller.py
│       └── ventilation_controller.py
├── hardware_interface/     # Abstraction matérielle
│   ├── base_hardware.py
│   ├── raspberry_pi.py
│   └── mock_hardware.py
└── utils/
    ├── db_utils.py        # Gestion base de données
    └── config.py          # Configuration
```

---

## 📊 Analyse de l'architecture actuelle

### ✅ Points forts

1. **Séparation des préoccupations** : Code organisé en modules distincts
2. **Abstraction matérielle** : Pattern Strategy déjà présent (mock/rpi)
3. **Gestion des threads** : Acquisition capteurs et logique métier séparées
4. **Configuration centralisée** : Fichier config.py avec gestion JSON
5. **Logging structuré** : Suivi des opérations à différents niveaux

### ⚠️ Points à améliorer

#### 1. **Violations SOLID**

**Single Responsibility Principle (SRP)**
- ❌ `SerreController` a trop de responsabilités :
  - Gestion des threads
  - Gestion de la configuration
  - Coordination des actionneurs
  - Lecture des capteurs
  - Communication avec la BD

**Open/Closed Principle (OCP)**
- ❌ Ajout d'un nouvel actionneur nécessite modification de `SerreController`
- ❌ Logique métier câblée en dur dans les contrôleurs d'actionneurs

**Dependency Inversion Principle (DIP)**
- ❌ Dépendances concrètes sur `DatabaseManager` et imports directs
- ⚠️ Couplage fort avec psycopg2

#### 2. **Architecture de la base de données**

**Problèmes actuels :**
- ❌ Une seule table `sensor_data` monolithique
- ❌ Pas de gestion d'utilisateurs ou de sessions
- ❌ Pas d'historique des commandes manuelles
- ❌ Pas de système d'alertes ou notifications
- ❌ Pas de traçabilité des modifications de configuration

**Structure actuelle :**
```sql
sensor_data (
    timestamp, temperature, humidity, co2,
    humidifier_active, ventilation_active, leds_active,
    humidifier_on_duration_seconds, humidifier_off_duration_seconds,
    ventilation_on_duration_seconds, ventilation_off_duration_seconds
)
```

#### 3. **API REST incomplète**

**Routes actuelles :**
- ✅ GET `/status` - État du système
- ✅ GET/POST `/api/settings` - Configurations
- ✅ POST `/control/*` - Contrôle manuel

**Manque :**
- ❌ Authentification/autorisation
- ❌ Pagination des données historiques
- ❌ Filtres et agrégations
- ❌ WebSocket pour temps réel
- ❌ Gestion des alertes
- ❌ Endpoints pour statistiques/analytics

---

## 🏗️ Principes SOLID et Design Patterns

### Principe 1 : Single Responsibility (SRP)

**Problème actuel :** `SerreController` fait tout

**Solution :** Découper en classes spécialisées

```python
# Avant : SerreController (527 lignes, 15+ responsabilités)

# Après : Architecture découplée
SerreOrchestrator          # Coordination générale
├── SensorAcquisitionService   # Lecture capteurs
├── ActuatorCoordinator        # Gestion actionneurs
├── ConfigurationManager       # Gestion config
├── DataPersistenceService     # Stockage BD
└── HealthMonitor              # Surveillance système
```

### Principe 2 : Open/Closed (OCP)

**Pattern : Strategy + Registry**

```python
# Stratégies d'actionneurs configurables
class ActuatorStrategy(ABC):
    @abstractmethod
    def should_activate(self, sensor_data: SensorData, config: dict) -> bool:
        pass

class TimeBasedStrategy(ActuatorStrategy):
    """Activation basée sur plages horaires (LEDs)"""
    pass

class ThresholdStrategy(ActuatorStrategy):
    """Activation basée sur seuils (Humidificateur, Ventilation)"""
    pass

# Registry pour enregistrement dynamique
ActuatorRegistry.register("leds", LedController, TimeBasedStrategy())
ActuatorRegistry.register("humidifier", HumidifierController, ThresholdStrategy())
```

### Principe 3 : Liskov Substitution (LSP)

**Application correcte de l'héritage**

```python
# Hiérarchie cohérente pour les actionneurs
BaseActuator (interface)
├── OnOffActuator (logique binaire)
│   ├── LedActuator
│   ├── VentilationActuator
│   └── HumidifierActuator
└── VariableActuator (contrôle variable - futur)
    └── PWMFanActuator
```

### Principe 4 : Interface Segregation (ISP)

**Interfaces spécifiques au lieu de grandes interfaces**

```python
# Au lieu d'une seule interface HardwareInterface
class ISensorReader(Protocol):
    def read_sensor(self) -> SensorData: ...

class IActuatorControl(Protocol):
    def activate(self): ...
    def deactivate(self): ...

class IGPIOControl(Protocol):
    def setup_pin(self, pin: int, mode: str): ...
    def set_output(self, pin: int, state: bool): ...
```

### Principe 5 : Dependency Inversion (DIP)

**Inversion des dépendances avec injection**

```python
# Avant
class SerreController:
    def __init__(self):
        self.db_manager = DatabaseManager()  # Dépendance concrète

# Après
class SerreOrchestrator:
    def __init__(
        self,
        sensor_service: ISensorService,
        persistence: IDataPersistence,
        actuator_coordinator: IActuatorCoordinator
    ):
        self._sensor_service = sensor_service
        self._persistence = persistence
        self._actuator_coordinator = actuator_coordinator
```

### Design Patterns recommandés

#### 1. **Strategy Pattern** ✅ Déjà partiellement présent
- Pour les différentes logiques d'activation des actionneurs
- Pour les différentes interfaces matérielles (mock/rpi)

#### 2. **Observer Pattern** 🆕 À ajouter
- Notifications des changements d'état capteurs
- Système d'alertes et événements

```python
class SensorEventPublisher:
    def __init__(self):
        self._observers: List[ISensorObserver] = []
    
    def subscribe(self, observer: ISensorObserver):
        self._observers.append(observer)
    
    def notify(self, event: SensorEvent):
        for observer in self._observers:
            observer.on_sensor_event(event)

# Utilisation
publisher.subscribe(AlertManager())
publisher.subscribe(DataLogger())
publisher.subscribe(ActuatorCoordinator())
```

#### 3. **Repository Pattern** 🆕 À ajouter
- Abstraction de la couche de persistance
- Facilite le changement de BD (PostgreSQL → autre)

```python
class ISensorDataRepository(Protocol):
    def save(self, data: SensorData) -> None: ...
    def get_latest(self) -> SensorData: ...
    def get_range(self, start: datetime, end: datetime) -> List[SensorData]: ...

class PostgresSensorDataRepository(ISensorDataRepository):
    # Implémentation PostgreSQL
    pass

class InMemorySensorDataRepository(ISensorDataRepository):
    # Pour les tests
    pass
```

#### 4. **Factory Pattern** 🆕 À ajouter
- Création d'actionneurs et services

```python
class ActuatorFactory:
    @staticmethod
    def create_actuator(
        actuator_type: str,
        hardware: IHardwareInterface,
        strategy: ActuatorStrategy
    ) -> BaseActuator:
        actuators = {
            "led": LedActuator,
            "ventilation": VentilationActuator,
            "humidifier": HumidifierActuator,
        }
        actuator_class = actuators.get(actuator_type)
        if not actuator_class:
            raise ValueError(f"Unknown actuator type: {actuator_type}")
        return actuator_class(hardware, strategy)
```

#### 5. **Command Pattern** 🆕 À ajouter
- Historique des commandes manuelles
- Système d'annulation (undo)

```python
class ActuatorCommand(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    
    @abstractmethod
    def undo(self) -> None: ...

class ActivateActuatorCommand(ActuatorCommand):
    def __init__(self, actuator: BaseActuator):
        self._actuator = actuator
        self._previous_state = None
    
    def execute(self):
        self._previous_state = self._actuator.current_state
        self._actuator.activate()
    
    def undo(self):
        if self._previous_state is not None:
            self._actuator.set_state(self._previous_state)
```

---

## 🔧 Plan de refactorisation

### Phase 1 : Restructuration du cœur applicatif (2-3 jours)

#### Étape 1.1 : Créer les services métier

**Fichiers à créer :**

```
src/core/services/
├── __init__.py
├── sensor_service.py          # Service d'acquisition capteurs
├── actuator_coordinator.py    # Coordination actionneurs
├── configuration_manager.py   # Gestion configuration
└── health_monitor.py          # Surveillance système
```

**Détails `sensor_service.py` :**

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass
class SensorData:
    timestamp: datetime
    temperature: float | None
    humidity: float | None
    co2: float | None
    is_valid: bool

class ISensorReader(Protocol):
    def read_sensor(self) -> tuple[float | None, float | None, float | None]: ...

class SensorAcquisitionService:
    """Service responsable de l'acquisition des données capteurs"""
    
    def __init__(self, hardware: ISensorReader, interval_seconds: int = 15):
        self._hardware = hardware
        self._interval = interval_seconds
        self._latest_data: SensorData | None = None
        self._observers: List[ISensorObserver] = []
        # Threading, etc.
    
    def get_latest_data(self) -> SensorData | None:
        return self._latest_data
    
    def subscribe(self, observer: ISensorObserver):
        self._observers.append(observer)
    
    def _acquisition_loop(self):
        # Logique d'acquisition en boucle
        pass
```

#### Étape 1.2 : Implémenter le pattern Repository

**Fichiers à créer :**

```
src/data/
├── __init__.py
├── repositories/
│   ├── __init__.py
│   ├── base.py              # Interfaces de base
│   ├── sensor_data_repo.py
│   ├── actuator_log_repo.py
│   └── alert_repo.py
└── models/
    ├── __init__.py
    ├── sensor_data.py
    ├── actuator_log.py
    └── alert.py
```

#### Étape 1.3 : Refactoriser SerreController → SerreOrchestrator

**Fichier à modifier :** `src/core/orchestrator.py` (nouveau)

```python
class SerreOrchestrator:
    """
    Orchestrateur principal - Coordination uniquement
    Applique le SRP en déléguant les responsabilités
    """
    def __init__(
        self,
        sensor_service: SensorAcquisitionService,
        actuator_coordinator: ActuatorCoordinator,
        config_manager: ConfigurationManager,
        data_repository: ISensorDataRepository
    ):
        self._sensor_service = sensor_service
        self._actuator_coordinator = actuator_coordinator
        self._config_manager = config_manager
        self._data_repository = data_repository
        
        # Abonnement aux événements
        self._sensor_service.subscribe(self._on_sensor_data)
    
    def _on_sensor_data(self, data: SensorData):
        """Callback lors de nouvelles données capteurs"""
        # Déléguer au coordinateur d'actionneurs
        self._actuator_coordinator.update(data)
        # Persister les données
        self._data_repository.save(data)
```

### Phase 2 : Optimisation de la base de données (1-2 jours)

#### Étape 2.1 : Nouvelle structure de BD

**Fichier à créer :** `schema_v2.sql`

```sql
-- =====================================================
-- SCHÉMA DE BASE DE DONNÉES V2
-- Serre Connectée - Optimisé pour mobile et analytics
-- =====================================================

-- 1. Table des données capteurs (optimisée)
CREATE TABLE sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    co2 REAL,
    data_quality VARCHAR(20) DEFAULT 'valid', -- 'valid', 'partial', 'invalid'
    
    -- Index pour requêtes temporelles
    CONSTRAINT sensor_readings_timestamp_idx UNIQUE (timestamp)
);

CREATE INDEX idx_sensor_readings_timestamp ON sensor_readings(timestamp DESC);
CREATE INDEX idx_sensor_readings_quality ON sensor_readings(data_quality) WHERE data_quality != 'valid';

-- 2. Table des états d'actionneurs (nouvelle)
CREATE TABLE actuator_states (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actuator_type VARCHAR(50) NOT NULL, -- 'led', 'humidifier', 'ventilation'
    is_active BOOLEAN NOT NULL,
    mode VARCHAR(20) NOT NULL, -- 'auto', 'manual'
    duration_seconds REAL,
    
    -- Contexte de la commande
    triggered_by VARCHAR(50), -- 'system', 'user', 'schedule', 'threshold'
    user_id INTEGER REFERENCES users(id), -- Si commande manuelle
    
    CONSTRAINT actuator_states_check CHECK (actuator_type IN ('led', 'humidifier', 'ventilation'))
);

CREATE INDEX idx_actuator_states_timestamp ON actuator_states(timestamp DESC);
CREATE INDEX idx_actuator_states_type ON actuator_states(actuator_type, timestamp DESC);

-- 3. Table des utilisateurs (nouvelle - pour mobile)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt
    role VARCHAR(20) DEFAULT 'user', -- 'admin', 'user', 'viewer'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- 4. Table des configurations (nouvelle)
CREATE TABLE configuration_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config_key VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT NOT NULL,
    changed_by INTEGER REFERENCES users(id),
    change_reason TEXT
);

CREATE INDEX idx_config_history_timestamp ON configuration_history(timestamp DESC);
CREATE INDEX idx_config_history_key ON configuration_history(config_key);

-- 5. Table des alertes (nouvelle)
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL, -- 'sensor_error', 'threshold_exceeded', 'system_error'
    severity VARCHAR(20) NOT NULL, -- 'info', 'warning', 'critical'
    message TEXT NOT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    
    -- Métadonnées supplémentaires (JSON)
    metadata JSONB
);

CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity) WHERE NOT is_acknowledged;
CREATE INDEX idx_alerts_acknowledged ON alerts(is_acknowledged);

-- 6. Table des sessions API (pour mobile)
CREATE TABLE api_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_api_sessions_token ON api_sessions(token);
CREATE INDEX idx_api_sessions_user ON api_sessions(user_id);
CREATE INDEX idx_api_sessions_expires ON api_sessions(expires_at) WHERE is_active;

-- 7. Vue agrégée pour statistiques (performance)
CREATE MATERIALIZED VIEW daily_statistics AS
SELECT 
    DATE(timestamp) as date,
    AVG(temperature) as avg_temperature,
    MIN(temperature) as min_temperature,
    MAX(temperature) as max_temperature,
    AVG(humidity) as avg_humidity,
    MIN(humidity) as min_humidity,
    MAX(humidity) as max_humidity,
    AVG(co2) as avg_co2,
    MIN(co2) as min_co2,
    MAX(co2) as max_co2,
    COUNT(*) as reading_count,
    COUNT(CASE WHEN data_quality = 'valid' THEN 1 END) as valid_reading_count
FROM sensor_readings
GROUP BY DATE(timestamp);

CREATE UNIQUE INDEX idx_daily_stats_date ON daily_statistics(date DESC);

-- Fonction pour rafraîchir les statistiques (à appeler périodiquement)
CREATE OR REPLACE FUNCTION refresh_daily_statistics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_statistics;
END;
$$ LANGUAGE plpgsql;

-- 8. Trigger pour nettoyer les anciennes données (optionnel)
CREATE OR REPLACE FUNCTION cleanup_old_sensor_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Garder seulement 90 jours de données détaillées
    DELETE FROM sensor_readings
    WHERE timestamp < NOW() - INTERVAL '90 days';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Créer un trigger quotidien (nécessite pg_cron ou exécution externe)
-- CREATE TRIGGER trigger_cleanup_sensor_data
-- AFTER INSERT ON sensor_readings
-- EXECUTE FUNCTION cleanup_old_sensor_data();
```

#### Étape 2.2 : Script de migration

**Fichier à créer :** `migrations/migrate_v1_to_v2.py`

```python
"""
Migration de la base de données V1 vers V2
Préserve les données existantes
"""

def migrate_sensor_data(old_conn, new_conn):
    """Migre sensor_data vers sensor_readings et actuator_states"""
    # Extraction données V1
    # Transformation
    # Insertion dans V2
    pass

def create_default_user(conn):
    """Crée l'utilisateur par défaut pour l'accès mobile"""
    pass

def run_migration():
    # Backup BD
    # Créer nouvelle structure
    # Migrer données
    # Valider
    pass
```

### Phase 3 : API REST complète (2-3 jours)

#### Étape 3.1 : Restructurer l'API Flask

**Nouvelle structure :**

```
src/api/
├── __init__.py
├── app.py                  # Application Flask principale
├── auth/                   # Authentification
│   ├── __init__.py
│   ├── middleware.py       # JWT validation
│   └── routes.py           # Login, logout, refresh
├── routes/                 # Routes organisées
│   ├── __init__.py
│   ├── status.py           # État système
│   ├── sensors.py          # Données capteurs
│   ├── actuators.py        # Contrôle actionneurs
│   ├── settings.py         # Configuration
│   ├── alerts.py           # Alertes
│   └── statistics.py       # Analytics
├── schemas/                # Validation Pydantic
│   ├── __init__.py
│   ├── sensor_data.py
│   ├── actuator_command.py
│   └── user.py
└── middleware/
    ├── __init__.py
    ├── auth.py
    └── rate_limit.py
```

#### Étape 3.2 : Endpoints API pour mobile

**Documentation OpenAPI/Swagger complète**

**Fichier à créer :** `src/api/routes/sensors.py`

```python
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from src.api.auth.middleware import require_auth
from src.data.repositories.sensor_data_repo import SensorDataRepository

sensors_bp = Blueprint('sensors', __name__, url_prefix='/api/v1/sensors')

@sensors_bp.route('/latest', methods=['GET'])
@require_auth
def get_latest_sensor_data():
    """
    Récupère la dernière lecture de capteurs
    
    Response:
    {
        "timestamp": "2025-09-30T12:34:56",
        "temperature": 22.5,
        "humidity": 78.2,
        "co2": 850,
        "quality": "valid"
    }
    """
    repo = SensorDataRepository()
    latest = repo.get_latest()
    return jsonify(latest.to_dict())

@sensors_bp.route('/history', methods=['GET'])
@require_auth
def get_sensor_history():
    """
    Récupère l'historique des capteurs avec pagination
    
    Query params:
    - start_date: ISO datetime (défaut: 24h avant)
    - end_date: ISO datetime (défaut: maintenant)
    - page: int (défaut: 1)
    - per_page: int (défaut: 100, max: 1000)
    - interval: str ('raw', 'minute', 'hour', 'day')
    
    Response:
    {
        "data": [...],
        "pagination": {
            "page": 1,
            "per_page": 100,
            "total": 2456,
            "pages": 25
        }
    }
    """
    # Parse query params
    start_date = request.args.get('start_date', 
                                   (datetime.now() - timedelta(days=1)).isoformat())
    end_date = request.args.get('end_date', datetime.now().isoformat())
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 100)), 1000)
    interval = request.args.get('interval', 'raw')
    
    repo = SensorDataRepository()
    result = repo.get_paginated_range(
        start=datetime.fromisoformat(start_date),
        end=datetime.fromisoformat(end_date),
        page=page,
        per_page=per_page,
        aggregation=interval
    )
    
    return jsonify(result)

@sensors_bp.route('/statistics', methods=['GET'])
@require_auth
def get_sensor_statistics():
    """
    Statistiques agrégées
    
    Query params:
    - period: 'day', 'week', 'month' (défaut: 'day')
    
    Response:
    {
        "period": "day",
        "start_date": "2025-09-30T00:00:00",
        "end_date": "2025-09-30T23:59:59",
        "temperature": {
            "avg": 22.3,
            "min": 18.5,
            "max": 26.1
        },
        "humidity": {...},
        "co2": {...}
    }
    """
    period = request.args.get('period', 'day')
    repo = SensorDataRepository()
    stats = repo.get_statistics(period)
    return jsonify(stats)
```

**Fichier à créer :** `src/api/auth/middleware.py`

```python
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({"error": "Missing authentication token"}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.user_role = payload['role']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### Phase 4 : Tests et validation (1-2 jours)

#### Étape 4.1 : Tests unitaires

**Fichiers à créer :**

```
tests/unit/
├── test_sensor_service.py
├── test_actuator_coordinator.py
├── test_repositories.py
└── test_strategies.py
```

#### Étape 4.2 : Tests d'intégration

```
tests/integration/
├── test_api_endpoints.py
├── test_database_operations.py
└── test_end_to_end.py
```

---

## 📱 API REST pour intégration mobile

### Endpoints complets

#### Authentification

```
POST   /api/v1/auth/login           # Connexion
POST   /api/v1/auth/logout          # Déconnexion
POST   /api/v1/auth/refresh         # Renouveler token
GET    /api/v1/auth/me              # Info utilisateur
```

#### Capteurs

```
GET    /api/v1/sensors/latest       # Dernière lecture
GET    /api/v1/sensors/history      # Historique paginé
GET    /api/v1/sensors/statistics   # Statistiques agrégées
GET    /api/v1/sensors/export       # Export CSV/JSON
```

#### Actionneurs

```
GET    /api/v1/actuators/status     # État de tous les actionneurs
POST   /api/v1/actuators/:type/control  # Contrôle manuel
GET    /api/v1/actuators/:type/history  # Historique d'activation
PUT    /api/v1/actuators/:type/mode     # Auto/Manuel
```

#### Configuration

```
GET    /api/v1/settings             # Toutes les configurations
PUT    /api/v1/settings             # Modifier configurations
GET    /api/v1/settings/history     # Historique modifications
```

#### Alertes

```
GET    /api/v1/alerts               # Liste des alertes
POST   /api/v1/alerts/:id/acknowledge  # Acquitter alerte
DELETE /api/v1/alerts/:id           # Supprimer alerte
```

#### WebSocket (temps réel)

```
WS     /ws/sensors                  # Stream données capteurs
WS     /ws/actuators                # Stream états actionneurs
WS     /ws/alerts                   # Stream alertes
```

### Format de réponse standardisé

```json
{
    "success": true,
    "data": {...},
    "error": null,
    "metadata": {
        "timestamp": "2025-09-30T12:34:56Z",
        "version": "v1",
        "request_id": "uuid"
    }
}
```

---

## 🗓️ Roadmap d'implémentation

### Semaine 1 : Refactorisation du cœur

| Jour | Tâche | Durée | Priorité |
|------|-------|-------|----------|
| 1 | Créer les services métier (sensor, actuator) | 4h | 🔴 Haute |
| 1 | Implémenter le pattern Repository | 4h | 🔴 Haute |
| 2 | Refactoriser SerreController → Orchestrator | 6h | 🔴 Haute |
| 2 | Tests unitaires des services | 2h | 🟡 Moyenne |
| 3 | Implémenter Strategy pattern pour actionneurs | 4h | 🔴 Haute |
| 3 | Implémenter Observer pattern | 4h | 🟡 Moyenne |
| 4 | Factory et Command patterns | 4h | 🟢 Basse |
| 4 | Refactoring complet + tests | 4h | 🔴 Haute |
| 5 | Buffer + validation | 8h | 🟡 Moyenne |

### Semaine 2 : Base de données et API

| Jour | Tâche | Durée | Priorité |
|------|-------|-------|----------|
| 1 | Créer nouveau schéma BD V2 | 4h | 🔴 Haute |
| 1 | Script de migration V1→V2 | 4h | 🔴 Haute |
| 2 | Tester migration sur données de test | 3h | 🔴 Haute |
| 2 | Exécuter migration en production | 1h | 🔴 Haute |
| 2 | Validation intégrité données | 2h | 🔴 Haute |
| 3 | Restructurer API Flask (blueprints) | 4h | 🔴 Haute |
| 3 | Implémenter authentification JWT | 4h | 🔴 Haute |
| 4 | Créer tous les endpoints REST | 6h | 🔴 Haute |
| 4 | Documenter API (OpenAPI/Swagger) | 2h | 🟡 Moyenne |
| 5 | Tests API + intégration | 6h | 🔴 Haute |
| 5 | Optimisation performances | 2h | 🟢 Basse |

### Semaine 3 : Tests et déploiement

| Jour | Tâche | Durée | Priorité |
|------|-------|-------|----------|
| 1 | Tests end-to-end complets | 6h | 🔴 Haute |
| 1-2 | Correction bugs identifiés | 4h | 🔴 Haute |
| 2 | WebSocket temps réel (optionnel) | 4h | 🟢 Basse |
| 3 | Documentation complète | 4h | 🟡 Moyenne |
| 3 | Guide d'intégration Flutter | 2h | 🟡 Moyenne |
| 4 | Déploiement sur Raspberry Pi | 3h | 🔴 Haute |
| 4-5 | Tests sur environnement réel | 5h | 🔴 Haute |
| 5 | Ajustements finaux | 3h | 🟡 Moyenne |

---

## ✅ Checklist de validation

### Code Quality

- [ ] Tous les principes SOLID respectés
- [ ] Design patterns correctement appliqués
- [ ] Code coverage > 80% pour les services critiques
- [ ] Pas de violation de linters (pylint, mypy)
- [ ] Documentation complète (docstrings)

### Base de données

- [ ] Migration V1→V2 réussie sans perte de données
- [ ] Index créés sur toutes les colonnes fréquemment requêtées
- [ ] Contraintes d'intégrité en place
- [ ] Plan de sauvegarde automatique configuré

### API

- [ ] Tous les endpoints testés et fonctionnels
- [ ] Authentification JWT sécurisée
- [ ] Rate limiting en place
- [ ] Documentation OpenAPI complète
- [ ] Gestion d'erreurs cohérente
- [ ] CORS configuré correctement

### Tests

- [ ] Tests unitaires pour tous les services
- [ ] Tests d'intégration pour l'API
- [ ] Tests end-to-end pour les scénarios critiques
- [ ] Tests de charge (performance)

### Déploiement

- [ ] Service systemd configuré
- [ ] Logs centralisés
- [ ] Monitoring en place
- [ ] Processus de rollback documenté

---

## 📚 Ressources complémentaires

### Documentation à créer

1. **ARCHITECTURE.md** : Diagrammes et explications détaillées
2. **API_REFERENCE.md** : Documentation complète de l'API
3. **FLUTTER_INTEGRATION.md** : Guide pour l'intégration mobile
4. **DEPLOYMENT.md** : Guide de déploiement et configuration
5. **CONTRIBUTING.md** : Guide pour les contributeurs

### Outils recommandés

- **Pydantic** : Validation de données et schémas
- **FastAPI** (alternative à Flask) : Performances + OpenAPI natif
- **SQLAlchemy** : ORM pour simplifier les requêtes BD
- **Alembic** : Migrations de BD versionnées
- **pytest-cov** : Coverage des tests
- **Black** : Formatage automatique du code
- **mypy** : Vérification de types statique

---

## 🎓 Prochaines étapes recommandées

1. **Lire ce document en entier** pour comprendre la vision globale
2. **Consulter l'oracle** pour valider l'architecture proposée
3. **Commencer par Phase 1, Étape 1.1** : Services métier
4. **Procéder étape par étape** en validant avec des tests
5. **Documenter les décisions** prises en cours de route

---

*Document créé le 30 septembre 2025*  
*Version 1.0 - Guide de refactorisation Serre Connectée*
