from datetime import datetime

from pydantic import BaseModel


class ScanTraceOut(BaseModel):
    id: int
    event_id: str
    device_mac: str
    rfid_uid: str | None = None
    scanned_at: datetime | None = None
    backend_received_at: datetime
    handler_started_at: datetime
    handler_finished_at: datetime | None = None
    outcome: str
    instrument_id: int | None = None
    from_room_id: int | None = None
    to_room_id: int | None = None
    error_code: str | None = None
    error_detail: str | None = None
    raw_topic: str
    raw_payload: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MetricStatsOut(BaseModel):
    count: int
    min_ms: float | None = None
    max_ms: float | None = None
    mean_ms: float | None = None
    median_ms: float | None = None
    p95_ms: float | None = None
    p99_ms: float | None = None


class DiagnosticsSummaryOut(BaseModel):
    total_events: int
    by_outcome: dict[str, int]
    esp_to_backend_ms: MetricStatsOut
    backend_processing_ms: MetricStatsOut
    end_to_end_ms: MetricStatsOut
