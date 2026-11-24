"""Debezium JSON envelope parsing helpers."""
from typing import Any


def parse_event(event: dict[str, Any]) -> dict[str, Any] | None:
    payload = event.get("payload", event)
    if not isinstance(payload, dict):
        return None
    operation = payload.get("op")
    if operation not in {"c", "u", "d", "r"}:
        return None
    row = payload.get("after") if operation != "d" else payload.get("before")
    if not isinstance(row, dict):
        return None
    source = payload.get("source") or {}
    return {
        "operation": operation,
        "table": source.get("table"),
        "ts_ms": payload.get("ts_ms"),
        "data": row,
    }
