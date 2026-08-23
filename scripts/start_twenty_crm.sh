#!/usr/bin/env bash
# ==============================================================================
# AgencyOS — Start Local Self-Hosted Twenty CRM (Open-Source)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================================================="
echo " Starting Open-Source Twenty CRM (http://localhost:3000)"
echo "=================================================================="

cd "$ROOT_DIR"

if command -v docker >/dev/null 2>&1; then
    echo "[INFO] Launching Twenty CRM containers via Docker Compose..."
    docker compose -f docker-compose.twenty.yml up -d
    echo "[INFO] Twenty CRM is spinning up on http://localhost:3000"
    echo "[INFO] Open http://localhost:3000 in your browser to complete initial admin setup."
else
    echo "[ERROR] Docker is not installed or running. Please install Docker to self-host Twenty CRM."
    exit 1
fi
