#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

#
# MULTI-TENANT FIX: Ensure psycopg2 driver is available before starting server
#
echo ">>> Verifying psycopg2 driver availability..."
PSYCOPG2_SRC="/usr/local/lib/python3.10/site-packages/psycopg2"
PSYCOPG2_DEST="/app/pythonpath/psycopg2"

if [ -d "$PSYCOPG2_SRC" ]; then
    if [ ! -L "$PSYCOPG2_DEST" ] && [ ! -d "$PSYCOPG2_DEST" ]; then
        ln -sf "$PSYCOPG2_SRC" "$PSYCOPG2_DEST"
        echo ">>> psycopg2 symlink created: $PSYCOPG2_DEST -> $PSYCOPG2_SRC"
    else
        echo ">>> psycopg2 already available in pythonpath"
    fi
else
    echo ">>> WARNING: psycopg2 not found at $PSYCOPG2_SRC"
fi

HYPHEN_SYMBOL='-'

gunicorn \
    --bind "${SUPERSET_BIND_ADDRESS:-0.0.0.0}:${SUPERSET_PORT:-8088}" \
    --access-logfile "${ACCESS_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --error-logfile "${ERROR_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --workers ${SERVER_WORKER_AMOUNT:-1} \
    --worker-class ${SERVER_WORKER_CLASS:-gthread} \
    --threads ${SERVER_THREADS_AMOUNT:-20} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --keep-alive ${GUNICORN_KEEPALIVE:-2} \
    --max-requests ${WORKER_MAX_REQUESTS:-0} \
    --max-requests-jitter ${WORKER_MAX_REQUESTS_JITTER:-0} \
    --limit-request-line ${SERVER_LIMIT_REQUEST_LINE:-0} \
    --limit-request-field_size ${SERVER_LIMIT_REQUEST_FIELD_SIZE:-0} \
    "${FLASK_APP}"
