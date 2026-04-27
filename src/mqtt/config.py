import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MqttSettings:
    host: str
    port: int
    username: str | None
    password: str | None
    scan_topic: str = "scanners/+/scan"
    status_topic: str = "scanners/+/status"
    client_id: str = "rfid-backend"
    dedupe_ttl_seconds: int = 300
    dedupe_max_entries: int = 10000


def load_settings() -> MqttSettings:
    return MqttSettings(
        host=os.getenv("MQTT_BROKER_HOST", "localhost"),
        port=int(os.getenv("MQTT_BROKER_PORT", "1883")),
        username=os.getenv("MQTT_USERNAME") or None,
        password=os.getenv("MQTT_PASSWORD") or None,
    )
