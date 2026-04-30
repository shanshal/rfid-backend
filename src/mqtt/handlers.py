import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.models.instrument import Instrument
from src.models.mqtt_scan_trace import MqttScanTrace
from src.mqtt.schemas import AnnounceEvent, ScanEvent, StatusEvent
from src.services.device_service import get_or_create_pending_device
from src.services.audit_service import write_audit_event
from src.services.errors import DomainError
from src.services.event_service import log_movement_event

log = logging.getLogger(__name__)


def _insert_scan_trace_start(
    event: ScanEvent,
    backend_received_at: datetime,
    raw_topic: str,
    raw_payload: str,
) -> int | None:
    db: Session = SessionLocal()
    try:
        trace = MqttScanTrace(
            event_id=event.event_id,
            device_mac=event.device_mac,
            rfid_uid=event.rfid_uid,
            scanned_at=event.scanned_at,
            backend_received_at=backend_received_at,
            handler_started_at=datetime.now(timezone.utc),
            outcome="processing",
            raw_topic=raw_topic,
            raw_payload=raw_payload,
        )
        db.add(trace)
        db.commit()
        db.refresh(trace)
        return trace.id
    except Exception:
        log.exception("failed to insert mqtt scan trace start")
        return None
    finally:
        db.close()


def _finalize_scan_trace(
    trace_id: int | None,
    *,
    outcome: str,
    instrument_id: int | None = None,
    from_room_id: int | None = None,
    to_room_id: int | None = None,
    error_code: str | None = None,
    error_detail: str | None = None,
) -> None:
    if trace_id is None:
        return
    db: Session = SessionLocal()
    try:
        trace = db.query(MqttScanTrace).filter(MqttScanTrace.id == trace_id).first()
        if trace is None:
            return
        trace.outcome = outcome
        trace.instrument_id = instrument_id
        trace.from_room_id = from_room_id
        trace.to_room_id = to_room_id
        trace.error_code = error_code
        trace.error_detail = error_detail[:500] if error_detail else None
        trace.handler_finished_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        log.exception("failed to finalize mqtt scan trace id=%s", trace_id)
    finally:
        db.close()


def handle_scan(
    event: ScanEvent,
    backend_received_at: datetime,
    raw_topic: str,
    raw_payload: str,
) -> None:
    trace_id = _insert_scan_trace_start(event, backend_received_at, raw_topic, raw_payload)
    db: Session = SessionLocal()
    outcome = "handler_error"
    instrument_id: int | None = None
    from_room_id: int | None = None
    to_room_id: int | None = None
    error_code: str | None = None
    error_detail: str | None = None
    try:
        device, created = get_or_create_pending_device(db, event.device_mac)
        if created:
            log.info("discovered new scanner mac=%s as pending device_id=%s", event.device_mac, device.id)
        device.last_activity_at = datetime.now(timezone.utc)

        if device.room_id is None:
            log.warning("scan from unassigned device mac=%s", event.device_mac)
            outcome = "unassigned_device"
            error_code = "device_unassigned_room"
            write_audit_event(
                db,
                event_type="device_unassigned_room",
                actor=f"scanner:{event.device_mac}",
                payload=event.model_dump(mode="json"),
            )
            db.commit()
            return

        instrument = (
            db.query(Instrument)
            .filter(Instrument.rfid == event.rfid_uid, Instrument.deleted_at.is_(None))
            .first()
        )
        if instrument is None:
            log.warning("scan with unknown rfid=%s on device=%s", event.rfid_uid, event.device_mac)
            outcome = "unknown_rfid"
            error_code = "unknown_rfid_scanned"
            write_audit_event(
                db,
                event_type="unknown_rfid_scanned",
                actor=f"scanner:{event.device_mac}",
                payload=event.model_dump(mode="json"),
            )
            db.commit()
            return

        if instrument.current_room == device.room_id:
            outcome = "ignored_same_room"
            instrument_id = instrument.id
            from_room_id = instrument.current_room
            to_room_id = device.room_id
            return

        previous_room_id = instrument.current_room
        try:
            log_movement_event(
                db,
                instrument_id=instrument.id,
                from_room_id=instrument.current_room,
                to_room_id=device.room_id,
                actor=f"scanner:{device.mac_address}",
                reason=None,
                procedure_id=None,
            )
            outcome = "moved"
            instrument_id = instrument.id
            from_room_id = previous_room_id
            to_room_id = device.room_id
        except DomainError as err:
            log.warning(
                "movement rejected instrument=%s to_room=%s reason=%s",
                instrument.id,
                device.room_id,
                err,
            )
            outcome = "movement_rejected"
            instrument_id = instrument.id
            from_room_id = previous_room_id
            to_room_id = device.room_id
            error_code = "movement_rejected"
            error_detail = str(err)
            write_audit_event(
                db,
                event_type="movement_rejected",
                actor=f"scanner:{device.mac_address}",
                payload={**event.model_dump(mode="json"), "error": str(err)},
            )
            db.commit()
    except Exception as err:
        error_code = "handler_error"
        error_detail = str(err)
        raise
    finally:
        db.close()
        _finalize_scan_trace(
            trace_id,
            outcome=outcome,
            instrument_id=instrument_id,
            from_room_id=from_room_id,
            to_room_id=to_room_id,
            error_code=error_code,
            error_detail=error_detail,
        )


def handle_status(event: StatusEvent) -> None:
    db: Session = SessionLocal()
    try:
        device, created = get_or_create_pending_device(db, event.device_mac)
        if created:
            log.info("discovered new scanner mac=%s from status", event.device_mac)
        device.last_activity_at = datetime.now(timezone.utc)
        device.last_status = event.status
        if event.firmware:
            device.firmware = event.firmware
        db.commit()
    finally:
        db.close()


def handle_announce(event: AnnounceEvent) -> None:
    db: Session = SessionLocal()
    try:
        device, created = get_or_create_pending_device(db, event.device_mac)
        if created:
            log.info("discovered new scanner mac=%s from announce", event.device_mac)

        device.last_activity_at = datetime.now(timezone.utc)
        if event.local_ip is not None:
            device.local_ip = event.local_ip
        if event.scan_topic is not None:
            device.scan_topic = event.scan_topic
        if event.status_topic is not None:
            device.status_topic = event.status_topic
        if event.mqtt_host is not None:
            device.mqtt_host = event.mqtt_host
        if event.mqtt_port is not None:
            device.mqtt_port = event.mqtt_port
        if event.firmware is not None:
            device.firmware = event.firmware
        db.commit()
    finally:
        db.close()
