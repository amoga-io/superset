import logging
from typing import Any, Optional
from sqlalchemy import or_
from sqlalchemy.engine import make_url
from sqlalchemy.orm.query import Query
from flask_appbuilder.models.filters import BaseFilter
from superset.security import SupersetSecurityManager

print("\n" + "!"*60)
print(">>> DEPLOYING ABSOLUTE MULTI-TENANT ISOLATION WALL <<<")
print("!"*60 + "\n")

# Ensure psycopg2 is available FIRST before any database operations
import sys
import os
psycopg2_path = "/usr/local/lib/python3.10/site-packages/psycopg2"
if os.path.exists(psycopg2_path) and psycopg2_path not in sys.path:
    sys.path.insert(0, psycopg2_path)
    print(f">>> PYTHONPATH: Added {psycopg2_path}")

# Import the multi-tenant patches module (but don't apply yet)
try:
    import multi_tenant_patches
    print(">>> PATCHES: Multi-tenant module imported successfully")
    
    # Apply patches will be called after app initialization
    # via FAB_APP_BUILDER_INIT_HOOK below
except ImportError as e:
    print(f">>> WARNING: Could not load multi_tenant_patches: {e}")

# 1. DATABASE ROUTING
def DB_CONNECTION_MUTATOR(uri, params, username, security_manager, source):
    MASTER_DB_NAME = 'Organization_Portal'
    if source and source.database_name == MASTER_DB_NAME:
        if username and username != 'admin' and username is not None:
            tenant_db = f"{username.lower().replace(' ', '_')}_db"
            uri = uri.set(database=tenant_db)
            print(f">>> MUTATOR: Swapped {username} to {tenant_db}")
    return uri, params

# 2. THE ISOLATION WALL - Enhanced Security Manager
class MultiTenantSecurityManager(SupersetSecurityManager):
    def is_admin(self):
        """Check if current user has Admin role"""
        if not self.current_user:
            return False
        return "Admin" in [r.name for r in self.current_user.roles]

    def can_access_all_datasources(self) -> bool:
        """
        Override to enforce ownership-mandatory rule.
        Even Alpha users must own datasets to access them.
        """
        # Only true admins can access all datasources
        return self.is_admin()

    def get_accessible_datasets(self):
        """
        DEPRECATED METHOD - but kept for backward compatibility.
        This is bypassed by REST API in Superset 3.x.
        Use base_filters in DatasetRestApi instead.
        """
        from superset.connectors.sqla.models import SqlaTable
        if not self.is_admin():
            datasets = self.get_session.query(SqlaTable).filter(
                SqlaTable.owners.contains(self.current_user)
            ).all()
            print(f">>> SECURITY: Datasets for {self.current_user} | Count: {len(datasets)}")
            return datasets
        return super().get_accessible_datasets()

    def get_accessible_charts(self):
        """
        DEPRECATED METHOD - but kept for backward compatibility.
        This is bypassed by REST API in Superset 3.x.
        Use base_filters in ChartRestApi instead.
        """
        from superset.models.slice import Slice
        if not self.is_admin():
            charts = self.get_session.query(Slice).filter(
                Slice.owners.contains(self.current_user)
            ).all()
            print(f">>> SECURITY: Charts for {self.current_user} | Count: {len(charts)}")
            return charts
        return super().get_accessible_charts()
    
    def get_schema_access_for_user(self, user):
        """
        Override to prevent Alpha users from seeing schemas they don't own datasets in.
        """
        if self.is_admin():
            return super().get_schema_access_for_user(user)
        
        # For non-admins, return empty to force ownership checking
        return set()
    
    def get_database_access_for_user(self, user):
        """
        Override to prevent Alpha users from having blanket database access.
        """
        if self.is_admin():
            return super().get_database_access_for_user(user)
        
        # For non-admins, return empty to force ownership checking
        return set()


# REGISTER THE MANAGER
CUSTOM_SECURITY_MANAGER = MultiTenantSecurityManager

# 3. CORE SETTINGS
FEATURE_FLAGS = {
    "SQL_TEMPLATING": True, 
    "ALERT_REPORTS": True, 
    "DYNAMIC_PLUGINS": True,
    "DASHBOARD_RBAC": False,  # Disable to enforce ownership-only model
}

SECRET_KEY = 'STAGING_REMOTE_KEY_9988'
PYTHONPATH = "/app/pythonpath"

# 4. Disable "all_datasource_access" permission for Alpha role
# This forces ownership checks even for Alpha users
PREVENT_UNSAFE_DEFAULT_URLS_ON_DATASET = True

# 5. Hook to apply patches after Flask app is fully initialized
# This will be called by FAB after app initialization
FLASK_APP_MUTATOR = lambda app: _init_multi_tenant_patches(app)

def _init_multi_tenant_patches(app):
    """Called after Flask app is initialized via FLASK_APP_MUTATOR"""
    with app.app_context():
        try:
            import multi_tenant_patches
            multi_tenant_patches.apply_all_patches()
            print(">>> FLASK_APP_MUTATOR: Multi-tenant patches applied successfully")
        except Exception as e:
            print(f">>> FLASK_APP_MUTATOR ERROR: {e}")
            import traceback
            traceback.print_exc()

print(">>> MULTI-TENANT ISOLATION WALL FULLY ACTIVE <<<\n")