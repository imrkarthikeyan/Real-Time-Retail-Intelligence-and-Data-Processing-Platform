from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QualityResult:
    valid: bool
    errors: tuple[str, ...]


def validate_order(record: dict[str, Any]) -> QualityResult:
    errors = []
    if not record.get("order_id"):
        errors.append("missing order_id")
    if float(record.get("total_amount", -1)) < 0:
        errors.append("negative total_amount")
    if record.get("order_status") not in {"pending", "confirmed", "shipped", "delivered", "cancelled"}:
        errors.append("invalid order_status")
    return QualityResult(not errors, tuple(errors))
