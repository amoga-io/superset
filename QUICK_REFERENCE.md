# Multi-Tenant Superset - Quick Reference Card

## 🚀 Quick Start

### Rebuild and Deploy
```bash
cd /home/ubuntu/superset
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Verify Installation
```bash
# Run verification script
docker exec -it superset_app bash /app/docker/verify-multi-tenant.sh

# Check logs for confirmation
docker logs superset_app 2>&1 | grep -E "PATCH|MUTATOR|SECURITY|psycopg2"
```

## 🔐 User Management

### Create Tenant User
```bash
docker exec -it superset_app superset fab create-user \
  --username tenant1_user \
  --firstname Tenant1 \
  --lastname User \
  --email tenant1@example.com \
  --password securepass123 \
  --role Alpha
```

### Create Admin User
```bash
docker exec -it superset_app superset fab create-admin \
  --username myadmin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password adminpass123
```

### Assign Dataset Ownership
```bash
# Via Python
docker exec -it superset_app python3 << 'EOF'
from superset import db
from superset.connectors.sqla.models import SqlaTable
from superset.models.core import User

# Get user and dataset
user = db.session.query(User).filter_by(username='tenant1_user').first()
dataset = db.session.query(SqlaTable).filter_by(table_name='my_table').first()

# Assign ownership
if user and dataset:
    dataset.owners.append(user)
    db.session.commit()
    print(f"✓ Assigned {dataset.table_name} to {user.username}")
EOF
```

## 🛠️ Troubleshooting

### Issue: "Driver psycopg2 not found"
```bash
# Verify symlink
docker exec superset_app ls -la /app/pythonpath/psycopg2

# Recreate symlink manually
docker exec -it --user root superset_app \
  ln -sf /usr/local/lib/python3.10/site-packages/psycopg2 /app/pythonpath/psycopg2

# Restart container
docker-compose restart superset_app
```

### Issue: Users see other tenants' data
```bash
# Check filter injection
docker exec superset_app python3 -c "
from superset.datasets.api import DatasetRestApi
print('Filters:', DatasetRestApi.base_filters)
"

# Check user ownership
docker exec superset_app python3 << 'EOF'
from superset import db
from superset.connectors.sqla.models import SqlaTable
from superset.models.core import User

user = db.session.query(User).filter_by(username='tenant1_user').first()
datasets = db.session.query(SqlaTable).filter(SqlaTable.owners.contains(user)).all()
print(f"Datasets for {user.username}: {[d.table_name for d in datasets]}")
EOF

# Verify admin status
docker exec superset_app python3 << 'EOF'
from superset import db
from superset.models.core import User

user = db.session.query(User).filter_by(username='suspect_user').first()
roles = [r.name for r in user.roles]
print(f"Roles: {roles}")
print(f"Is Admin: {'Admin' in roles}")
EOF
```

### Issue: Patches not loading
```bash
# Check file exists
docker exec superset_app ls -la /app/pythonpath_dev/multi_tenant_patches.py

# Test import
docker exec superset_app python3 -c "import multi_tenant_patches; print('OK')"

# Check logs
docker logs superset_app 2>&1 | grep "PATCH"
```

## 📊 Testing Isolation

### Test Dataset Visibility
```bash
# Create test script
cat > /tmp/test_isolation.py << 'EOF'
from superset import db, security_manager
from superset.connectors.sqla.models import SqlaTable
from superset.models.core import User
from flask import g

# Test user 1
user1 = db.session.query(User).filter_by(username='tenant1_user').first()
g.user = user1

# Check what tenant1 sees
datasets = db.session.query(SqlaTable).filter(SqlaTable.owners.contains(user1)).all()
print(f"\nTenant1 sees: {[d.table_name for d in datasets]}")

# Test user 2
user2 = db.session.query(User).filter_by(username='tenant2_user').first()
g.user = user2

datasets = db.session.query(SqlaTable).filter(SqlaTable.owners.contains(user2)).all()
print(f"Tenant2 sees: {[d.table_name for d in datasets]}")

# They should have no overlap
EOF

docker exec -i superset_app python3 < /tmp/test_isolation.py
```

### Test API Filtering
```bash
# Get auth token
TOKEN=$(docker exec superset_app python3 << 'EOF'
from superset.utils import json
from superset.security import login_manager
from superset import app

with app.app_context():
    # Your token generation logic here
    print("YOUR_TOKEN")
EOF
)

# Test dataset API
curl -X GET "http://localhost:8088/api/v1/dataset/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.result | length'
```

## 📝 Common Tasks

### List All Users and Their Datasets
```bash
docker exec superset_app python3 << 'EOF'
from superset import db
from superset.models.core import User
from superset.connectors.sqla.models import SqlaTable

users = db.session.query(User).all()
for user in users:
    datasets = db.session.query(SqlaTable).filter(SqlaTable.owners.contains(user)).all()
    print(f"\n{user.username}:")
    for d in datasets:
        print(f"  - {d.table_name}")
EOF
```

### Remove All Ownership (Reset)
```bash
docker exec superset_app python3 << 'EOF'
from superset import db
from superset.connectors.sqla.models import SqlaTable

datasets = db.session.query(SqlaTable).all()
for dataset in datasets:
    dataset.owners = []
db.session.commit()
print(f"✓ Removed ownership from {len(datasets)} datasets")
EOF
```

### Bulk Assign Ownership
```bash
docker exec superset_app python3 << 'EOF'
from superset import db
from superset.models.core import User
from superset.connectors.sqla.models import SqlaTable

# Get user
user = db.session.query(User).filter_by(username='tenant1_user').first()

# Assign all datasets with 'tenant1_' prefix
datasets = db.session.query(SqlaTable).filter(
    SqlaTable.table_name.like('tenant1_%')
).all()

for dataset in datasets:
    if user not in dataset.owners:
        dataset.owners.append(user)

db.session.commit()
print(f"✓ Assigned {len(datasets)} datasets to {user.username}")
EOF
```

## 🔍 Monitoring

### Check Multi-Tenant Health
```bash
# View recent logs
docker logs superset_app --tail 100 | grep -E "MUTATOR|FILTER|SECURITY"

# Monitor live
docker logs superset_app -f | grep --color -E "MUTATOR|FILTER|SECURITY|ERROR"

# Count filter applications
docker logs superset_app | grep "FILTER:" | wc -l
```

### Database Connection Checks
```bash
# Verify DB routing is working
docker exec superset_app python3 << 'EOF'
from superset import app
from superset.extensions import db as superset_db

# Check current config
config = app.config
mutator = config.get('DB_CONNECTION_MUTATOR')
print(f"DB_CONNECTION_MUTATOR active: {mutator is not None}")
EOF
```

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `/app/pythonpath/superset_config.py` | Main configuration |
| `/app/pythonpath_dev/multi_tenant_patches.py` | REST API filters |
| `/app/docker/docker-init.sh` | Container initialization |
| `/app/docker/run-server.sh` | Server startup script |
| `/app/docker/verify-multi-tenant.sh` | Verification script |

## 📞 Emergency Recovery

### Restore Admin Access
```bash
# Reset admin password
docker exec -it superset_app superset fab reset-password \
  --username admin \
  --password newpassword123

# Grant all permissions
docker exec superset_app superset init
```

### Disable Multi-Tenant (Emergency)
```bash
# Rename config to disable
docker exec --user root superset_app \
  mv /app/pythonpath/superset_config.py /app/pythonpath/superset_config.py.disabled

# Restart
docker-compose restart superset_app
```

---

**Version**: 1.0
**Last Updated**: December 29, 2025
**Support**: Check MULTI_TENANT_IMPLEMENTATION.md for details
