#!/usr/bin/env bash
# ==============================================================================
# AgencyOS — Start All Backend Microservices
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
    source "$ROOT_DIR/.venv/bin/activate"
fi

exec "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/start_backend_services.py"
