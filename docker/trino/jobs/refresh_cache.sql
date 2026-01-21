-- Trino Cache Refresh Job
-- This file runs every 15 minutes via cron
-- Add your materialized table refresh queries below

-- Example: Create schema if not exists
CREATE SCHEMA IF NOT EXISTS hive.cache;

-- Example: Refresh a daily metrics cache table
-- Uncomment and modify for your use case:

-- DROP TABLE IF EXISTS hive.cache.daily_metrics;
-- CREATE TABLE hive.cache.daily_metrics
-- WITH (format = 'PARQUET')
-- AS SELECT
--     date_trunc('day', created_at) as day,
--     COUNT(*) as total_count
-- FROM postgresql.public.your_table
-- GROUP BY 1;

-- Example: Refresh memory cache (fast, but lost on restart)
-- DROP TABLE IF EXISTS memory.default.hot_data;
-- CREATE TABLE memory.default.hot_data AS
-- SELECT * FROM postgresql.public.recent_data
-- WHERE updated_at > current_timestamp - interval '1' hour;

-- Log completion
SELECT 'Cache refresh completed at ' || cast(current_timestamp as varchar);
