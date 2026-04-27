from collections import Counter
from datetime import datetime
import math
import statistics

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.mqtt_scan_trace import MqttScanTrace
from src.schemas.diagnostics import DiagnosticsSummaryOut, MetricStatsOut, ScanTraceOut

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    rank = max(1, math.ceil((percentile / 100) * len(sorted_values)))
    return sorted_values[rank - 1]


def _stats(values: list[float]) -> MetricStatsOut:
    if not values:
        return MetricStatsOut(count=0)
    return MetricStatsOut(
        count=len(values),
        min_ms=min(values),
        max_ms=max(values),
        mean_ms=statistics.fmean(values),
        median_ms=statistics.median(values),
        p95_ms=_percentile(values, 95),
        p99_ms=_percentile(values, 99),
    )


def _base_trace_query(
    db: Session,
    start_at: datetime | None,
    end_at: datetime | None,
    device_mac: str | None,
    outcome: str | None,
):
    query = db.query(MqttScanTrace)
    if start_at is not None:
        query = query.filter(MqttScanTrace.backend_received_at >= start_at)
    if end_at is not None:
        query = query.filter(MqttScanTrace.backend_received_at <= end_at)
    if device_mac:
        query = query.filter(MqttScanTrace.device_mac == device_mac)
    if outcome:
        query = query.filter(MqttScanTrace.outcome == outcome)
    return query


@router.get("/traces", response_model=list[ScanTraceOut])
def list_scan_traces(
    limit: int = Query(default=200, ge=1, le=5000),
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    device_mac: str | None = None,
    outcome: str | None = None,
    db: Session = Depends(get_db),
):
    query = _base_trace_query(db, start_at, end_at, device_mac, outcome)
    return query.order_by(MqttScanTrace.backend_received_at.desc()).limit(limit).all()


@router.get("/summary", response_model=DiagnosticsSummaryOut)
def get_diagnostics_summary(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    device_mac: str | None = None,
    outcome: str | None = None,
    db: Session = Depends(get_db),
):
    rows = (
        _base_trace_query(db, start_at, end_at, device_mac, outcome)
        .order_by(MqttScanTrace.backend_received_at.asc())
        .all()
    )

    outcome_counts = dict(Counter(row.outcome for row in rows))

    esp_to_backend_ms: list[float] = []
    backend_processing_ms: list[float] = []
    end_to_end_ms: list[float] = []

    for row in rows:
        if row.scanned_at is not None:
            esp_to_backend_ms.append((row.backend_received_at - row.scanned_at).total_seconds() * 1000)

        if row.handler_finished_at is not None:
            backend_processing_ms.append(
                (row.handler_finished_at - row.handler_started_at).total_seconds() * 1000
            )

        if row.scanned_at is not None and row.handler_finished_at is not None:
            end_to_end_ms.append((row.handler_finished_at - row.scanned_at).total_seconds() * 1000)

    return DiagnosticsSummaryOut(
        total_events=len(rows),
        by_outcome=outcome_counts,
        esp_to_backend_ms=_stats(esp_to_backend_ms),
        backend_processing_ms=_stats(backend_processing_ms),
        end_to_end_ms=_stats(end_to_end_ms),
    )
