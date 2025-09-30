# Architecture du Projet

## Structure des Fichiers

```
Projet_IoT_RaspberryPi/
│
├── main.py                              # Point d'entrée principal
├── requirements.txt                     # Dépendances Python
├── serre.service                        # Service systemd pour démarrage auto
├── .gitignore                          # Fichiers ignorés par Git
│
├── data/                               # Données et configuration
│   ├── serre.db                        # Base SQLite (auto-créée)
│   ├── user_settings.json              # Configuration utilisateur modifiable
│   └── logs/
│       └── serre_controller.log        # Logs de l'application
│
├── src/                                # Code source
│   ├── config.py                       # Configuration centrale
│   │
│   ├── core/                           # Logique métier
│   │   ├── orchestrator.py             # Orchestrateur principal (coordonne tout)
│   │   ├── actuators/                  # Contrôleurs d'actionneurs
│   │   │   ├── led_controller.py       # Gestion LEDs
│   │   │   ├── humidifier_controller.py # Gestion humidificateur
│   │   │   └── ventilation_controller.py # Gestion ventilation
│   │   └── services/                   # Services métier (SRP)
│   │       ├── sensor_service.py       # Acquisition capteurs en arrière-plan
│   │       ├── actuator_coordinator.py # Coordination actionneurs (thread-safe)
│   │       ├── configuration_manager.py # Gestion configuration (JSON + defaults)
│   │       └── data_persistence_service.py # Sauvegarde base de données
│   │
│   ├── hardware_interface/             # Abstraction matérielle
│   │   ├── raspberry_pi.py             # Interface GPIO/I2C réelle (lgpio + SCD30)
│   │   └── mock_hardware.py            # Simulation pour développement
│   │
│   ├── api/                            # API REST
│   │   └── monitoring_api.py           # FastAPI - Monitoring + Contrôle
│   │
│   └── utils/                          # Utilitaires
│       ├── cli_menu.py                 # Menu interactif terminal
│       ├── db_utils.py                 # Gestionnaire PostgreSQL
│       └── db_utils_sqlite.py          # Gestionnaire SQLite
│
├── scripts/                            # Scripts utilitaires
│   ├── hardware_test_menu.py           # Test manuel du matériel
│   ├── start_web.sh                    # Démarrage API standalone
│   ├── stop_all.sh                     # Arrêt tous processus Python
│   └── Donnees.sql                     # Schéma PostgreSQL (optionnel)
│
├── tests/                              # Tests automatisés
│   ├── core/                           # Tests logique métier
│   ├── hardware_interface/             # Tests interfaces matérielles
│   └── utils/                          # Tests utilitaires
│
└── docs/                               # Documentation
    ├── 1-fundation/                    # Documentation de base
    ├── 2-logic/                        # Documentation logique métier
    ├── 3-api/                          # Documentation API
    ├── legacy/                         # Fichiers obsolètes archivés
    ├── API_ELECTRON.md                 # Guide pour app Electron
    └── REFACTORING_GUIDE.md            # Architecture SOLID détaillée
```

## Principe de l'Architecture

Le projet suit une **architecture SOLID modulaire** :

- **Orchestrator** (`orchestrator.py`) : Coordonne tous les services. Il ne fait QUE coordonner, pas de logique métier.
- **Services** : Chaque service a une responsabilité unique (acquisition capteurs, coordination actionneurs, persistence, configuration).
- **Abstraction matérielle** : `RaspberryPiHardware` ou `MockHardware` peuvent être utilisés de manière interchangeable.
- **API** : L'orchestrateur est injecté dans l'API FastAPI pour permettre le contrôle à distance.

L'application peut tourner en **mode mock** (simulation) ou **mode réel** (GPIO/I2C), configuré via la variable d'environnement `HARDWARE_ENV`.
