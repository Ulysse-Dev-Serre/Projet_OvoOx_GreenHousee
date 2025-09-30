#!/bin/bash
# Script de test de l'API
# Usage: bash scripts/test_api.sh [IP] [API_KEY]

# Configuration
API_URL="${1:-http://localhost:5000}"
API_KEY="${2:-test-key}"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🧪 Test de l'API Serre Connectée"
echo "=========================================="
echo "URL: $API_URL"
echo "API Key: $API_KEY"
echo ""

# Fonction pour tester un endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local auth=$5
    
    echo -n "Testing $method $endpoint ... "
    
    if [ "$auth" = "true" ]; then
        headers="-H 'X-API-Key: $API_KEY'"
    else
        headers=""
    fi
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            $headers \
            -d "$data" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            $headers 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
        echo "   $description"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "   Error: $body"
        return 1
    fi
}

# Fonction pour vérifier la présence d'une clé dans JSON
check_json_key() {
    local json=$1
    local key=$2
    
    if echo "$json" | grep -q "\"$key\""; then
        return 0
    else
        return 1
    fi
}

# Compteurs
total=0
passed=0
failed=0

echo "📡 Tests de lecture (sans authentification)"
echo "-------------------------------------------"

# Test 1: Health check
total=$((total + 1))
echo -n "1. GET /health ... "
response=$(curl -s "$API_URL/health")
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✓ OK${NC}"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
    failed=$((failed + 1))
fi

# Test 2: Root endpoint
total=$((total + 1))
echo -n "2. GET / ... "
response=$(curl -s "$API_URL/")
if echo "$response" | grep -q "Serre"; then
    echo -e "${GREEN}✓ OK${NC}"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
    failed=$((failed + 1))
fi

# Test 3: Status endpoint
total=$((total + 1))
echo -n "3. GET /api/status (avec durées) ... "
response=$(curl -s "$API_URL/api/status")
has_temp=$(echo "$response" | grep -q "temperature"; echo $?)
has_leds=$(echo "$response" | grep -q "leds"; echo $?)
has_on_duration=$(echo "$response" | grep -q "on_duration_seconds"; echo $?)
has_off_duration=$(echo "$response" | grep -q "off_duration_seconds"; echo $?)

if [ $has_temp -eq 0 ] && [ $has_leds -eq 0 ] && [ $has_on_duration -eq 0 ] && [ $has_off_duration -eq 0 ]; then
    echo -e "${GREEN}✓ OK${NC} (température + actionneurs + durées présents)"
    passed=$((passed + 1))
else
    echo -e "${YELLOW}⚠ PARTIAL${NC}"
    [ $has_temp -ne 0 ] && echo "   ✗ température manquante"
    [ $has_leds -ne 0 ] && echo "   ✗ actionneurs manquants"
    [ $has_on_duration -ne 0 ] && echo "   ✗ on_duration_seconds manquant"
    [ $has_off_duration -ne 0 ] && echo "   ✗ off_duration_seconds manquant"
    failed=$((failed + 1))
fi

# Test 4: Settings endpoint
total=$((total + 1))
echo -n "4. GET /api/settings (avec horaires opération) ... "
response=$(curl -s "$API_URL/api/settings")
has_led_hours=$(echo "$response" | grep -q "HEURE_DEBUT_LEDS"; echo $?)
has_op_hours=$(echo "$response" | grep -q "HEURE_DEBUT_JOUR_OPERATION"; echo $?)
has_co2=$(echo "$response" | grep -q "SEUIL_CO2_MAX"; echo $?)

if [ $has_led_hours -eq 0 ] && [ $has_op_hours -eq 0 ] && [ $has_co2 -eq 0 ]; then
    echo -e "${GREEN}✓ OK${NC} (7 paramètres présents)"
    passed=$((passed + 1))
else
    echo -e "${YELLOW}⚠ PARTIAL${NC}"
    [ $has_led_hours -ne 0 ] && echo "   ✗ HEURE_DEBUT_LEDS manquant"
    [ $has_op_hours -ne 0 ] && echo "   ✗ HEURE_DEBUT_JOUR_OPERATION manquant"
    [ $has_co2 -ne 0 ] && echo "   ✗ SEUIL_CO2_MAX manquant"
    failed=$((failed + 1))
fi

# Test 5: History endpoint
total=$((total + 1))
echo -n "5. GET /api/history?limit=5 ... "
response=$(curl -s "$API_URL/api/history?limit=5")
if echo "$response" | grep -q "data"; then
    echo -e "${GREEN}✓ OK${NC}"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
    failed=$((failed + 1))
fi

echo ""
echo "🔐 Tests de contrôle (avec authentification)"
echo "--------------------------------------------"

# Test 6: Contrôle LEDs (sans auth - devrait échouer)
total=$((total + 1))
echo -n "6. POST /api/control/leds (sans auth) ... "
response=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/control/leds" \
    -H "Content-Type: application/json" \
    -d '{"manual_mode": true, "state": true}' | tail -n1)
if [ "$response" = "401" ]; then
    echo -e "${GREEN}✓ OK${NC} (rejeté comme attendu)"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC} (devrait être 401, obtenu $response)"
    failed=$((failed + 1))
fi

# Test 7: Contrôle LEDs (avec auth - devrait réussir)
total=$((total + 1))
echo -n "7. POST /api/control/leds (avec auth) ... "
response=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/control/leds" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"manual_mode": false}' | tail -n1)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (autorisé)"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
    failed=$((failed + 1))
fi

# Test 8: Mode AUTO
total=$((total + 1))
echo -n "8. POST /api/control/auto (avec auth) ... "
response=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/control/auto" \
    -H "X-API-Key: $API_KEY" | tail -n1)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC}"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
    failed=$((failed + 1))
fi

# Test 9: Modifier settings (sans auth - devrait échouer)
total=$((total + 1))
echo -n "9. PUT /api/settings (sans auth) ... "
response=$(curl -s -w "%{http_code}" -X PUT "$API_URL/api/settings" \
    -H "Content-Type: application/json" \
    -d '{"settings": {"SEUIL_CO2_MAX": 1300}}' | tail -n1)
if [ "$response" = "401" ]; then
    echo -e "${GREEN}✓ OK${NC} (rejeté comme attendu)"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAILED${NC} (devrait être 401, obtenu $response)"
    failed=$((failed + 1))
fi

echo ""
echo "=========================================="
echo "📊 Résultats"
echo "=========================================="
echo "Total:  $total tests"
echo -e "Passés: ${GREEN}$passed${NC}"
echo -e "Échoués: ${RED}$failed${NC}"

if [ $failed -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Tous les tests sont passés !${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
    exit 1
fi
