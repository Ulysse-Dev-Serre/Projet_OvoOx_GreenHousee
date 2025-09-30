#!/usr/bin/env python3
"""
Script de test simple de l'API
Usage: python scripts/test_api_simple.py [URL] [API_KEY]
"""

import sys
import requests
import json
from typing import Dict, Any

# Configuration
API_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
API_KEY = sys.argv[2] if len(sys.argv) > 2 else "test-key"

# Couleurs
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class APITester:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def test(self, name: str, func):
        """Execute un test et affiche le résultat"""
        self.total += 1
        print(f"{self.total}. {name} ... ", end='')
        try:
            result, message = func()
            if result:
                print(f"{GREEN}✓ OK{NC}")
                if message:
                    print(f"   {message}")
                self.passed += 1
            else:
                print(f"{RED}✗ FAILED{NC}")
                if message:
                    print(f"   {message}")
                self.failed += 1
        except Exception as e:
            print(f"{RED}✗ ERROR{NC}")
            print(f"   {str(e)}")
            self.failed += 1
    
    def print_summary(self):
        """Affiche le résumé des tests"""
        print("\n" + "="*50)
        print("📊 Résultats")
        print("="*50)
        print(f"Total:  {self.total} tests")
        print(f"Passés: {GREEN}{self.passed}{NC}")
        print(f"Échoués: {RED}{self.failed}{NC}")
        
        if self.failed == 0:
            print(f"\n{GREEN}✅ Tous les tests sont passés !{NC}")
            return 0
        else:
            print(f"\n{RED}❌ {self.failed} test(s) ont échoué{NC}")
            return 1
    
    # Tests individuels
    
    def test_health(self):
        """Test /health"""
        r = requests.get(f"{self.base_url}/health")
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'healthy':
                return True, f"Version: {data.get('version')}"
        return False, f"HTTP {r.status_code}"
    
    def test_root(self):
        """Test /"""
        r = requests.get(f"{self.base_url}/")
        if r.status_code == 200:
            data = r.json()
            if 'Serre' in data.get('name', ''):
                return True, None
        return False, f"HTTP {r.status_code}"
    
    def test_status_with_durations(self):
        """Test /api/status avec on_duration et off_duration"""
        r = requests.get(f"{self.base_url}/api/status")
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        
        data = r.json()
        
        # Vérifier la présence des données de base
        if 'temperature' not in data:
            return False, "Température manquante"
        
        # Vérifier les actionneurs
        for actuator in ['leds', 'humidifier', 'ventilation']:
            if actuator not in data:
                return False, f"{actuator} manquant"
            
            # Vérifier les durées
            if 'on_duration_seconds' not in data[actuator]:
                return False, f"{actuator}.on_duration_seconds manquant"
            if 'off_duration_seconds' not in data[actuator]:
                return False, f"{actuator}.off_duration_seconds manquant"
        
        return True, "Température + actionneurs + durées présents"
    
    def test_settings_with_operation_hours(self):
        """Test /api/settings avec HEURE_DEBUT/FIN_JOUR_OPERATION"""
        r = requests.get(f"{self.base_url}/api/settings")
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        
        data = r.json()
        
        required_keys = [
            'HEURE_DEBUT_LEDS',
            'HEURE_FIN_LEDS',
            'SEUIL_HUMIDITE_ON',
            'SEUIL_HUMIDITE_OFF',
            'SEUIL_CO2_MAX',
            'HEURE_DEBUT_JOUR_OPERATION',
            'HEURE_FIN_JOUR_OPERATION'
        ]
        
        missing = [key for key in required_keys if key not in data]
        
        if missing:
            return False, f"Clés manquantes: {', '.join(missing)}"
        
        return True, "7 paramètres présents"
    
    def test_history(self):
        """Test /api/history"""
        r = requests.get(f"{self.base_url}/api/history?limit=5")
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        
        data = r.json()
        if 'data' not in data:
            return False, "Clé 'data' manquante"
        
        return True, f"{len(data['data'])} entrées retournées"
    
    def test_control_without_auth(self):
        """Test POST /api/control/leds sans authentification (devrait échouer)"""
        r = requests.post(
            f"{self.base_url}/api/control/leds",
            json={"manual_mode": True, "state": True}
        )
        
        if r.status_code == 401:
            return True, "Rejeté comme attendu (401)"
        
        return False, f"Devrait être 401, obtenu {r.status_code}"
    
    def test_control_with_auth(self):
        """Test POST /api/control/leds avec authentification"""
        r = requests.post(
            f"{self.base_url}/api/control/leds",
            headers={"X-API-Key": self.api_key},
            json={"manual_mode": False}
        )
        
        if r.status_code == 200:
            return True, "Autorisé (200)"
        
        return False, f"HTTP {r.status_code}"
    
    def test_auto_mode(self):
        """Test POST /api/control/auto"""
        r = requests.post(
            f"{self.base_url}/api/control/auto",
            headers={"X-API-Key": self.api_key}
        )
        
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                return True, None
        
        return False, f"HTTP {r.status_code}"
    
    def test_update_settings_without_auth(self):
        """Test PUT /api/settings sans auth (devrait échouer)"""
        r = requests.put(
            f"{self.base_url}/api/settings",
            json={"settings": {"SEUIL_CO2_MAX": 1300}},
            timeout=5
        )
        
        if r.status_code == 401:
            return True, "Rejeté comme attendu (401)"
        
        return False, f"Devrait être 401, obtenu {r.status_code}"
    
    def run_all_tests(self):
        """Execute tous les tests"""
        print("="*50)
        print("🧪 Test de l'API Serre Connectée")
        print("="*50)
        print(f"URL: {self.base_url}")
        print(f"API Key: {self.api_key[:8]}...")
        print()
        
        # Vérification préalable de la connexion
        print("🔍 Vérification de la connexion à l'API...")
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"{GREEN}✓ API accessible{NC}\n")
        except requests.exceptions.Timeout:
            print(f"{RED}✗ Timeout (5s) - L'API ne répond pas{NC}")
            print(f"{YELLOW}Vérifiez que 'python main.py' est démarré{NC}\n")
            return 1
        except requests.exceptions.ConnectionError:
            print(f"{RED}✗ Connexion refusée{NC}")
            print(f"{YELLOW}Vérifiez que 'python main.py' est démarré sur {self.base_url}{NC}\n")
            return 1
        except Exception as e:
            print(f"{RED}✗ Erreur: {e}{NC}\n")
            return 1
        
        print(f"{BLUE}📡 Tests de lecture (sans authentification){NC}")
        print("-"*50)
        self.test("GET /health", self.test_health)
        self.test("GET /", self.test_root)
        self.test("GET /api/status (avec durées)", self.test_status_with_durations)
        self.test("GET /api/settings (7 paramètres)", self.test_settings_with_operation_hours)
        self.test("GET /api/history", self.test_history)
        
        print()
        print(f"{BLUE}🔐 Tests de contrôle (avec authentification){NC}")
        print("-"*50)
        self.test("POST /api/control/leds (sans auth)", self.test_control_without_auth)
        self.test("POST /api/control/leds (avec auth)", self.test_control_with_auth)
        self.test("POST /api/control/auto", self.test_auto_mode)
        self.test("PUT /api/settings (sans auth)", self.test_update_settings_without_auth)
        
        return self.print_summary()


if __name__ == "__main__":
    print(f"\n{YELLOW}Note: Assurez-vous que l'API est démarrée (python main.py){NC}\n")
    
    tester = APITester(API_URL, API_KEY)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
