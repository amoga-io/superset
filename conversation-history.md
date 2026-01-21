# Superset + Trino Setup Conversation

## Summary

Added Trino as a data caching and transformation layer to Apache Superset, with a self-contained Docker deployment.

---

## User Request

> Can we add Trino to Superset here which configures with Superset?

## What is Trino?

Trino (formerly PrestoSQL) is a distributed SQL query engine for fast, interactive analytics:

- **Query data where it lives** - connects to multiple data sources without storing data itself
- **Federated queries** - join data across different systems in a single query
- **Speed** - in-memory, parallel processing across distributed nodes
- **No ETL needed** - query data directly without moving it to a data warehouse

### Use Case with Superset

User wanted Trino as a **caching and transformation layer**:
- **Data sources**: Databases (PostgreSQL, MySQL, etc.)
- **Deployment**: Docker Compose
- **Caching**: Both materialized tables + query result caching

---

## Architecture

```
┌──────────────┐
│   Superset   │
└──────┬───────┘
       │ trino://trino:8085
       ▼
┌──────────────────────────────────────────────────┐
│                     Trino                         │
│  ┌─────────────┬─────────────┬─────────────────┐ │
│  │  postgresql │   memory    │      hive       │ │
│  │  (sources)  │ (hot cache) │ (materialized)  │ │
│  └──────┬──────┴──────┬──────┴────────┬────────┘ │
└─────────┼─────────────┼───────────────┼──────────┘
          ▼             ▼               ▼
    Your Databases   In-Memory      MinIO (S3)
    (Postgres/MySQL)                Parquet files
```

---

## Services Added

| Service | Port | Purpose |
|---------|------|---------|
| `trino` | 8085 | Query engine with caching |
| `hive-metastore` | 9083 | Metadata for materialized tables |
| `metastore-db` | - | PostgreSQL for Hive metadata |
| `minio` | 9000, 9001 | S3 storage for cached data |
| `trino-scheduler` | - | Cron job (every 15 min) to refresh cache |

---

## Files Created

### 1. Added to main `docker-compose.yml`

Trino services integrated directly into `/Users/joy/dev/superset/docker-compose.yml`

### 2. Trino Configuration (`docker/trino/`)

```
docker/trino/
├── etc/
│   ├── config.properties      # Query caching enabled
│   ├── node.properties
│   ├── jvm.config
│   ├── log.properties
│   └── catalog/
│       ├── postgresql.properties   # Query Superset's PostgreSQL
│       ├── memory.properties       # In-memory cache
│       ├── hive.properties         # Persistent cache (MinIO)
│       ├── external_postgres.properties.example
│       └── mysql.properties.example
└── jobs/
    └── refresh_cache.sql      # Scheduled refresh queries
```

---

## Self-Contained Production Setup

User requested a portable setup that could be copied to another location.

### Created: `/Users/joy/dev/infra-scripts/docker/superset/`

Self-contained folder using pre-built images (`apache/superset:latest`):

```
superset/
├── docker-compose.yml                    # Main compose file
├── .env                                  # Environment config
├── docker-entrypoint-initdb.d/
│   └── examples-init.sh                  # Creates examples DB
├── pythonpath_dev/
│   ├── superset_config.py                # Superset config
│   └── superset_config_local.example     # Config template
└── trino/
    ├── etc/
    │   ├── config.properties
    │   ├── node.properties
    │   ├── jvm.config
    │   ├── log.properties
    │   └── catalog/
    │       ├── postgresql.properties
    │       ├── memory.properties
    │       ├── hive.properties
    │       ├── external_postgres.properties.example
    │       └── mysql.properties.example
    └── jobs/
        └── refresh_cache.sql
```

**15 files total** - cleaned up all unnecessary dev/test scripts.

### Differences from Dev Setup

| Aspect | Dev (root) | Production (docker/superset/) |
|--------|------------|-------------------------------|
| Images | Builds from source | Pre-built `apache/superset:latest` |
| Portability | Needs full repo | Self-contained folder |
| Hot reload | Yes | No |

---

## Usage

### Development (from superset root)

```bash
docker compose up -d
```

### Production (self-contained)

```bash
cd /Users/joy/dev/infra-scripts/docker/superset
docker compose up -d
```

### Connect Superset to Trino

1. Go to **Settings** → **Database Connections** → **+ Database**
2. Select **Trino**
3. SQLAlchemy URI: `trino://trino@trino:8085/hive`

---

## Using Trino for Transformations & Caching

### Create Transformed Views

```sql
CREATE VIEW hive.default.user_summary AS
SELECT
    date_trunc('day', created_at) as day,
    COUNT(*) as new_users
FROM postgresql.public.users
GROUP BY 1;
```

### Create Cached/Materialized Tables

```sql
-- Persistent cache in Hive (stored in MinIO)
CREATE TABLE hive.default.daily_metrics
WITH (format = 'PARQUET')
AS SELECT
    date_trunc('day', event_time) as day,
    COUNT(*) as events
FROM postgresql.public.events
GROUP BY 1;

-- Fast in-memory cache (lost on restart)
CREATE TABLE memory.default.hot_data AS
SELECT * FROM postgresql.public.recent_orders
WHERE order_date > current_date - interval '7' day;
```

### Configure Refresh Jobs

Edit `docker/trino/jobs/refresh_cache.sql`:

```sql
-- Runs every 15 minutes
DROP TABLE IF EXISTS hive.cache.my_aggregates;
CREATE TABLE hive.cache.my_aggregates
WITH (format = 'PARQUET')
AS SELECT
    date_trunc('day', timestamp) as day,
    COUNT(*) as events
FROM postgresql.public.your_source_table
GROUP BY 1;
```

---

## Access Points

| Service | URL |
|---------|-----|
| Superset | http://localhost:8088 |
| Trino | http://localhost:8085 |
| MinIO Console | http://localhost:9001 |

---

## For Production Security

Update `.env` with secure values:

```bash
SUPERSET_SECRET_KEY=$(openssl rand -base64 42)
DATABASE_PASSWORD=<strong-password>
POSTGRES_PASSWORD=<strong-password>
```
