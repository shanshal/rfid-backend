import asyncio
import logging
from datetime import datetime, timezone

import aiomqtt
from cachetools import TTLCache
from pydantic import ValidationError

from src.mqtt.config import MqttSettings
from src.mqtt.handlers import handle_scan, handle_status
from src.mqtt.schemas import ScanEvent, StatusEvent

log = logging.getLogger(__name__)


async def run_consumer(settings: MqttSettings, stop: asyncio.Event) -> None:
    seen_event_ids: TTLCache = TTLCache(
        maxsize=settings.dedupe_max_entries,
        ttl=settings.dedupe_ttl_seconds,
    )

    while not stop.is_set():
        try:
            async with aiomqtt.Client(
                hostname=settings.host,
                port=settings.port,
                username=settings.username,
                password=settings.password,
                identifier=settings.client_id,
            ) as client:
                log.info("MQTT consumer connected to %s:%s", settings.host, settings.port)
                await client.subscribe(settings.scan_topic, qos=1)
                await client.subscribe(settings.status_topic, qos=1)
                log.info("subscribed to %s and %s", settings.scan_topic, settings.status_topic)

                async for message in client.messages:
                    await _dispatch(message, seen_event_ids)
                    if stop.is_set():
                        break
        except aiomqtt.MqttError as err:
            if stop.is_set():
                break
            log.warning("MQTT connection lost (%s); retrying in 5s", err)
            try:
                await asyncio.wait_for(stop.wait(), timeout=5)
            except asyncio.TimeoutError:
                continue


async def _dispatch(message: "aiomqtt.Message", seen_event_ids: TTLCache) -> None:
    topic = message.topic.value
    payload = message.payload
    if isinstance(payload, (bytes, bytearray)):
        raw = bytes(payload)
    else:
        log.warning("dropping non-bytes payload on %s", topic)
        return

    try:
        if topic.endswith("/scan"):
            backend_received_at = datetime.now(timezone.utc)
            event = ScanEvent.model_validate_json(raw)
            if event.event_id in seen_event_ids:
                log.debug("dedupe drop event_id=%s", event.event_id)
                return
            seen_event_ids[event.event_id] = True
            raw_payload = raw.decode("utf-8", errors="replace")
            await asyncio.to_thread(handle_scan, event, backend_received_at, topic, raw_payload)
        elif topic.endswith("/status"):
            event = StatusEvent.model_validate_json(raw)
            await asyncio.to_thread(handle_status, event)
        else:
            log.debug("unhandled topic %s", topic)
    except ValidationError as err:
        log.warning("invalid payload on %s: %s", topic, err)
    except Exception:
        log.exception("handler error on %s", topic)
