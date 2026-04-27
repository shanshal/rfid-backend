#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

if [[ ! -f "${ROOT_DIR}/mqtt/passwords" ]]; then
  cat <<'EOF'
Missing mqtt/passwords file.

Create broker users first (from repo root):

  cp mqtt/passwords.example mqtt/passwords
  docker run --rm -v "$PWD/mqtt":/work eclipse-mosquitto:2 mosquitto_passwd -c /work/passwords scanner
  docker run --rm -v "$PWD/mqtt":/work eclipse-mosquitto:2 mosquitto_passwd /work/passwords backend

Then set backend MQTT password in .env:

  cp .env.example .env
  # edit BACKEND_MQTT_PASSWORD in .env
EOF
  exit 1
fi

if [[ -z "${BACKEND_MQTT_PASSWORD:-}" ]]; then
  cat <<'EOF'
BACKEND_MQTT_PASSWORD is not set.

Set it in .env (recommended) or your shell environment.
Example:

  cp .env.example .env
  # edit BACKEND_MQTT_PASSWORD in .env
EOF
  exit 1
fi

docker compose -f "${ROOT_DIR}/docker-compose.yml" up -d
docker compose -f "${ROOT_DIR}/docker-compose.yml" ps
