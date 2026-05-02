from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.mqtt_scan_trace import MqttScanTrace

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    time: datetime
    acknowledged: bool


@router.get("/", response_model=list[AlertOut])
def list_alerts(limit: int = 200, db: Session = Depends(get_db)):
    traces = (
        db.query(MqttScanTrace)
        .filter(MqttScanTrace.outcome == "unknown_rfid")
        .order_by(MqttScanTrace.backend_received_at.desc())
        .limit(limit)
        .all()
    )
    return [
        AlertOut(
            id=t.id,
            type="warning",
            title="Unknown RFID Tag",
            message=f"Unknown RFID Tag '{t.rfid_uid}'",
            time=t.backend_received_at,
            acknowledged=False,
        )
        for t in traces
    ]


@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    return {"id": alert_id, "acknowledged": True}
