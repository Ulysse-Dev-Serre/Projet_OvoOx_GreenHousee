# 📝 Journal des modifications

## Version 2.0.0 - 30 septembre 2025

### 🎯 Refactorisation majeure - Principe SRP appliqué

#### Architecture
- ✅ **SerreController** (533 lignes) → **5 services spécialisés** (~900 lignes bien organisées)
- ✅ Création de `SerreOrchestrator` (pattern de coordination)
- ✅ Pattern Observer implémenté pour les événements capteurs
- ✅ Injection de dépendances pour meilleure testabilité

#### Services créés
- `SensorAcquisitionService` - Acquisition capteurs uniquement
- `ConfigurationManager` - Gestion configuration uniquement
- `ActuatorCoordinator` - Coordination actionneurs uniquement
- `DataPersistenceService` - Persistence base de données uniquement

#### Base de données
- ✅ Support SQLite ajouté (pas besoin de PostgreSQL pour les tests)
- ✅ Adaptateur `SQLiteDatabaseManager` créé
- ✅ Sélection dynamique SQLite/PostgreSQL via `DB_TYPE`

#### Interface utilisateur
- ✅ Menu CLI interactif ajouté (`src/utils/cli_menu.py`)
- ✅ Contrôle manuel des appareils depuis le terminal
- ✅ Affichage temps réel (temp, humidité, CO2, état appareils)

#### API
- ✅ Migration Flask → FastAPI
- ✅ Documentation Swagger automatique (`/docs`)
- ✅ Endpoints standardisés avec Pydantic
- ✅ CORS configuré pour mobile/desktop

#### Matériel
- 🐛 **Résolu :** Erreur I/O errno 121 du capteur SCD30
  - Délais d'initialisation optimisés
  - Retry automatique (3 tentatives)
  - Réinitialisation du bus I2C en cas d'erreur

#### Organisation du projet
- ✅ Dossier `scripts/` créé (scripts utilitaires)
- ✅ Dossier `docs/` réorganisé (fundation/logic/api)
- ✅ Fichiers temporaires nettoyés
- ✅ Structure professionnelle

#### Documentation
- ✅ `CORE_LOGIC.md` - Guide simple de la logique (éducatif)
- ✅ `API_GUIDE.md` - Guide d'utilisation de l'API
- ✅ `ARCHITECTURE_SRP.md` - Architecture technique détaillée
- ✅ `INSTALLATION.md` - Guide d'installation complet
- ✅ `QUICK_START.md` - Démarrage rapide

#### Tests
- ✅ `tests/test_srp_refactoring.py` - Validation de la refactorisation
- ✅ `tests/test_hardware.py` - Tests du matériel
- ✅ Tous les tests passent ✅

### Fichiers modifiés
- `main.py` - Utilise `SerreOrchestrator`, menu CLI, nettoyage auto
- `src/core/actuators/*.py` - Adaptés pour `ConfigurationManager`
- `src/config.py` - Support `DB_TYPE` (sqlite/postgres)
- `src/hardware_interface/raspberry_pi.py` - Correction initialisation SCD30

### Fichiers créés
- `src/core/orchestrator.py`
- `src/core/services/sensor_service.py`
- `src/core/services/configuration_manager.py`
- `src/core/services/actuator_coordinator.py`
- `src/core/services/data_persistence_service.py`
- `src/utils/cli_menu.py`
- `src/utils/db_utils_sqlite.py`
- `src/api/app.py` (FastAPI)

### Fichiers supprimés/renommés
- `src/api/app.py` (Flask) → `app_flask_old.py` (backup)
- Fichiers temporaires supprimés (`.lgd-nfy0`, `__init__.py`, `fake/`)

---

## Version 1.0.0 - Avant refactorisation

Architecture initiale avec `SerreController` monolithique.

---

*Dernière mise à jour : 30 septembre 2025*
