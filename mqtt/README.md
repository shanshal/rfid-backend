# MQTT broker

Mosquitto runs in Docker and brokers messages between the ESP32 scanners and the FastAPI backend.

## First-time setup

Generate the password file (one-time):

```bash
cp passwords.example passwords
docker run --rm -v "$PWD":/work eclipse-mosquitto:2 \
  mosquitto_passwd -c /work/passwords scanner
docker run --rm -v "$PWD":/work eclipse-mosquitto:2 \
  mosquitto_passwd /work/passwords backend
```

`passwords` is gitignored; only `passwords.example` is committed.

## Run

From repo root:

```bash
scripts/stack-up.sh
```

Stop:

```bash
scripts/stack-down.sh
```

The root `docker-compose.yml` starts both Mosquitto and the FastAPI backend.

Set the scanner's MQTT credentials in the ESP32 setup portal to match the `scanner`
user in `mqtt/passwords`, and set `BACKEND_MQTT_PASSWORD` to match the `backend`
user password.

Broker listens on `tcp://<host>:1883`.

## Topics

- `scanners/{mac}/scan` — published by scanner per tag read (QoS 1).
- `scanners/{mac}/status` — boot, heartbeat, LWT (QoS 1, retained).

`{mac}` is the full uppercase MAC with colons, e.g. `AA:BB:CC:DD:EE:FF`.

## Debug

Watch all scanner traffic:

```bash
mosquitto_sub -h localhost -u backend -P <pw> -t 'scanners/#' -v
```

Hand-publish a fake scan:

```bash
mosquitto_pub -h localhost -u scanner -P <pw> \
  -t scanners/AA:BB:CC:DD:EE:FF/scan \
  -m '{"event_id":"x-1-1","device_mac":"AA:BB:CC:DD:EE:FF","rfid_uid":"0A0042F3B2","scanned_at":"2026-04-26T12:34:56Z"}'
```
