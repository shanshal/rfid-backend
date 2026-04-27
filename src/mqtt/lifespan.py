import asyncio
import logging
from contextlib import asynccontextmanager

from src.mqtt.client import run_consumer
from src.mqtt.config import load_settings

log = logging.getLogger(__name__)


@asynccontextmanager
async def mqtt_lifespan():
    settings = load_settings()
    stop = asyncio.Event()
    task = asyncio.create_task(run_consumer(settings, stop), name="mqtt-consumer")
    try:
        yield
    finally:
        stop.set()
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass
        log.info("MQTT consumer stopped")
