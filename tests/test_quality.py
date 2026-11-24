from retailpulse.quality.rules import validate_order


def test_valid_order():
    result = validate_order({"order_id": 1, "total_amount": 10, "order_status": "delivered"})
    assert result.valid


def test_invalid_order_is_reported():
    result = validate_order({"order_id": 1, "total_amount": -1, "order_status": "unknown"})
    assert not result.valid
    assert "negative total_amount" in result.errors
