# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
import sys
from typing import Any

from celery.schedules import crontab
from flask import g
from flask_appbuilder.models.sqla.filters import BaseFilter
from flask_caching.backends.filesystemcache import FileSystemCache
from sqlalchemy.orm import Query

logger = logging.getLogger()

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_DB = os.getenv("DATABASE_DB")

EXAMPLES_USER = os.getenv("EXAMPLES_USER")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT")
EXAMPLES_DB = os.getenv("EXAMPLES_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

SQLALCHEMY_EXAMPLES_URI = (
    f"{DATABASE_DIALECT}://"
    f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
    f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

# Feature flags - includes embedded superset and tenant isolation features
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "EMBEDDED_SUPERSET": True,
    "PUBLIC_DASHBOARD_ACCESS": True,
    "ALLOW_ADHOC_SUBQUERY": True,
    "DASHBOARD_RBAC": True,  # Enable role-based dashboard access control
}

# API resources enabled for embedded superset
ENABLED_API_RESOURCES = [
    "roles",
    "me",
    "security",
    "dashboard",
]

# Guest token configuration from environment variables (for embedded superset)
GUEST_TOKEN_JWT_SECRET = os.getenv("GUEST_TOKEN_JWT_SECRET", "")
GUEST_ROLE_NAME = os.getenv("GUEST_ROLE_NAME", "Public")

# Public role settings for embedded superset guest access
PUBLIC_ROLE_LIKE = "Gamma"
PUBLIC_ROLE_LIKE_GAMMA = True

# CORS settings for embedded superset (allows frontend apps to call Superset API)
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite fallback port
        "http://localhost:3000",  # Common dev port
        "http://localhost:3001",  # Express backend server
    ],
}

# NOTE: Iframe embedding headers (X-Frame-Options, CSP frame-ancestors) are handled
# by nginx in docker/nginx/templates/superset.conf.template
# This is more reliable than trying to configure Talisman

# Timezone configuration
DEFAULT_TIMEZONE = os.getenv("SUPERSET_DEFAULT_TIMEZONE", "UTC")

ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = "http://superset:8088/"
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL
SQLLAB_CTAS_NO_LIMIT = True

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)


# =============================================================================
# MULTI-TENANT ISOLATION: Strict Ownership-Based Access Control
# =============================================================================
# Regular users (including admins) only see resources they own.
# Guest token users (embedded superset):
#   - Can access Dashboards (your app layer controls which ones)
#   - Cannot list Charts or Datasets (strict ownership)
# =============================================================================


def _is_guest_user() -> bool:
    """Check if current user is a guest token user (embedded superset)."""
    try:
        from superset import security_manager

        return security_manager.is_guest_user()
    except Exception:
        return False


class StrictOwnershipFilter(BaseFilter):
    """
    Strict ownership filter for Datasets and Charts.
    ALL users (including admins and guest tokens) are filtered by ownership.
    No bypasses - you must own the resource to see it.
    """

    def apply(self, query: Query, value: Any) -> Query:
        # For regular users (including admins) - filter by ownership
        if hasattr(g, "user") and g.user and hasattr(g.user, "id"):
            user_id = g.user.id
            return query.filter(self.model.owners.any(id=user_id))

        # No authenticated user = no results
        return query.filter(False)


class DashboardOwnershipFilter(BaseFilter):
    """
    Ownership filter for Dashboards with guest token bypass.
    - Regular users (including admins): Only see dashboards they own
    - Guest token users: Bypass filter (your app layer controls embedding)
    """

    def apply(self, query: Query, value: Any) -> Query:
        # Guest users bypass dashboard ownership filter
        # Your application layer controls which dashboards get embedded
        if _is_guest_user():
            return query

        # For regular users (including admins) - filter by ownership
        if hasattr(g, "user") and g.user and hasattr(g.user, "id"):
            user_id = g.user.id
            return query.filter(self.model.owners.any(id=user_id))

        # No authenticated user = no results
        return query.filter(False)


# Import Superset security classes (deferred to avoid circular imports)
def _get_security_manager_class():
    from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
    from superset.exceptions import SupersetSecurityException
    from superset.security import SupersetSecurityManager

    class StrictOwnershipSecurityManager(SupersetSecurityManager):
        """
        Security manager that enforces strict ownership-based isolation.
        Regular users (including admins) can only see resources they own.
        Guest token users can access dashboards (controlled by your app layer).
        """

        def can_access_all_datasources(self) -> bool:
            """Nobody can access all datasources - must be owner."""
            return False

        def can_access_all_databases(self) -> bool:
            """Nobody can access all databases - must be owner."""
            return False

        def raise_for_ownership(self, resource: Any) -> None:
            """
            Override to remove admin bypass for regular users.
            Guest token users can access dashboards only.
            """
            # Guest users can access dashboards (embedding use case)
            # But not other resources
            if self.is_guest_user():
                from superset.models.dashboard import Dashboard

                if isinstance(resource, Dashboard):
                    return  # Allow dashboard access for guests
                # Block guest access to non-dashboard resources
                raise SupersetSecurityException(
                    SupersetError(
                        error_type=SupersetErrorType.MISSING_OWNERSHIP_ERROR,
                        message="Guest users can only access dashboards",
                        level=ErrorLevel.ERROR,
                    )
                )

            # For regular users - strict ownership required
            if hasattr(resource, "owners") and self.current_user in resource.owners:
                return

            raise SupersetSecurityException(
                SupersetError(
                    error_type=SupersetErrorType.MISSING_OWNERSHIP_ERROR,
                    message="You don't have ownership of this resource",
                    level=ErrorLevel.ERROR,
                )
            )

    return StrictOwnershipSecurityManager


# Deferred loading of security manager
CUSTOM_SECURITY_MANAGER = _get_security_manager_class()


def FLASK_APP_MUTATOR(app):
    """
    Inject ownership filters into REST APIs at startup.

    Filter strategy:
    - Datasets API: Strict ownership (no guest bypass)
    - Charts API: Strict ownership (no guest bypass)
    - Dashboards API: Ownership with guest bypass (for embedding)
    """
    from superset.charts.api import ChartRestApi
    from superset.dashboards.api import DashboardRestApi
    from superset.datasets.api import DatasetRestApi

    # Strict ownership for datasets and charts (no guest bypass)
    strict_filter = ["id", StrictOwnershipFilter, lambda: []]
    DatasetRestApi.base_filters.append(strict_filter)
    ChartRestApi.base_filters.append(strict_filter)

    # Dashboard filter with guest bypass for embedding
    dashboard_filter = ["id", DashboardOwnershipFilter, lambda: []]
    DashboardRestApi.base_filters.append(dashboard_filter)

    app.logger.info(">>> MULTI-TENANT ISOLATION: Filters injected")
    app.logger.info(">>>   Datasets/Charts: Strict ownership (no guest bypass)")
    app.logger.info(">>>   Dashboards: Ownership with guest bypass for embedding")


# =============================================================================
# END MULTI-TENANT ISOLATION
# =============================================================================


if os.getenv("CYPRESS_CONFIG") == "true":
    # When running the service as a cypress backend, we need to import the config
    # located @ tests/integration_tests/superset_test_config.py
    base_dir = os.path.dirname(__file__)
    module_folder = os.path.abspath(
        os.path.join(base_dir, "../../tests/integration_tests/")
    )
    sys.path.insert(0, module_folder)
    from superset_test_config import *  # noqa

    sys.path.pop(0)

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa: F403

    logger.info(
        f"Loaded your Docker configuration at [{superset_config_docker.__file__}]"
    )
except ImportError:
    logger.info("Using default Docker config...")
