#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

BACKEND_MQTT_PASSWORD="${BACKEND_MQTT_PASSWORD:-10203040}"
SCANNER_MQTT_PASSWORD="${SCANNER_MQTT_PASSWORD:-10203040}"
export BACKEND_MQTT_PASSWORD
export SCANNER_MQTT_PASSWORD

if [[ ! -f "${ROOT_DIR}/mqtt/passwords" ]]; then
  docker run --rm -v "${ROOT_DIR}/mqtt":/work eclipse-mosquitto:2 \
    sh -c "mosquitto_passwd -b -c /work/passwords scanner \"${SCANNER_MQTT_PASSWORD}\" && mosquitto_passwd -b /work/passwords backend \"${BACKEND_MQTT_PASSWORD}\""
fi

docker compose -f "${ROOT_DIR}/docker-compose.yml" up -d
docker compose -f "${ROOT_DIR}/docker-compose.yml" ps
