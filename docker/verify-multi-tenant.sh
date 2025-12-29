#!/bin/bash
# Multi-Tenant Superset Verification Script
# Run this inside the Docker container to verify all patches are working

echo "=========================================="
echo "Multi-Tenant Superset Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check psycopg2 availability
echo "1. Checking psycopg2 driver..."
if python3 -c "import psycopg2; print(f'   ✓ psycopg2 version: {psycopg2.__version__}')" 2>/dev/null; then
    echo -e "   ${GREEN}✓ psycopg2 is available${NC}"
else
    echo -e "   ${RED}✗ psycopg2 NOT available${NC}"
fi
echo ""

# Test 2: Check symlink
echo "2. Checking psycopg2 symlink..."
if [ -L "/app/pythonpath/psycopg2" ]; then
    TARGET=$(readlink -f /app/pythonpath/psycopg2)
    echo -e "   ${GREEN}✓ Symlink exists: /app/pythonpath/psycopg2 -> $TARGET${NC}"
else
    echo -e "   ${RED}✗ Symlink does not exist${NC}"
fi
echo ""

# Test 3: Check multi_tenant_patches module
echo "3. Checking multi_tenant_patches module..."
if python3 -c "import multi_tenant_patches" 2>/dev/null; then
    echo -e "   ${GREEN}✓ multi_tenant_patches module loaded${NC}"
else
    echo -e "   ${RED}✗ multi_tenant_patches module NOT found${NC}"
fi
echo ""

# Test 4: Check REST API filters injection
echo "4. Checking REST API filter injection..."
python3 << 'PYEOF'
try:
    from superset.datasets.api import DatasetRestApi
    from superset.charts.api import ChartRestApi
    
    dataset_filters = DatasetRestApi.base_filters
    chart_filters = ChartRestApi.base_filters
    
    print(f"   DatasetRestApi.base_filters: {dataset_filters}")
    print(f"   ChartRestApi.base_filters: {chart_filters}")
    
    if dataset_filters and chart_filters:
        print("   ✓ Filters are injected")
    else:
        print("   ✗ Filters NOT injected")
except Exception as e:
    print(f"   ✗ Error checking filters: {e}")
PYEOF
echo ""

# Test 5: Check custom security manager
echo "5. Checking custom security manager..."
python3 << 'PYEOF'
try:
    from superset import app
    config = app.config
    
    custom_sm = config.get('CUSTOM_SECURITY_MANAGER')
    if custom_sm:
        print(f"   ✓ CUSTOM_SECURITY_MANAGER: {custom_sm.__name__}")
    else:
        print("   ✗ CUSTOM_SECURITY_MANAGER not configured")
except Exception as e:
    print(f"   ✗ Error: {e}")
PYEOF
echo ""

# Test 6: Check DB_CONNECTION_MUTATOR
echo "6. Checking DB_CONNECTION_MUTATOR..."
python3 << 'PYEOF'
try:
    from superset import app
    config = app.config
    
    mutator = config.get('DB_CONNECTION_MUTATOR')
    if mutator and callable(mutator):
        print(f"   ✓ DB_CONNECTION_MUTATOR is configured")
    else:
        print("   ✗ DB_CONNECTION_MUTATOR not configured")
except Exception as e:
    print(f"   ✗ Error: {e}")
PYEOF
echo ""

# Test 7: Check feature flags
echo "7. Checking feature flags..."
python3 << 'PYEOF'
try:
    from superset import app
    config = app.config
    
    feature_flags = config.get('FEATURE_FLAGS', {})
    dashboard_rbac = feature_flags.get('DASHBOARD_RBAC')
    
    print(f"   DASHBOARD_RBAC: {dashboard_rbac}")
    
    if dashboard_rbac == False:
        print("   ✓ DASHBOARD_RBAC correctly disabled")
    else:
        print("   ⚠ DASHBOARD_RBAC should be False for ownership-only model")
except Exception as e:
    print(f"   ✗ Error: {e}")
PYEOF
echo ""

echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "If all checks passed, multi-tenant isolation is active."
echo "Run this command to test with a specific user:"
echo ""
echo "  docker exec -it superset_app superset fab create-user \\"
echo "    --username testuser --firstname Test --lastname User \\"
echo "    --email test@test.com --password test --role Alpha"
echo ""
