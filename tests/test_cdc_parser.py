from retailpulse.streaming.cdc_parser import parse_event


def test_debezium_create_event():
    event = {"payload": {"op": "c", "ts_ms": 10, "after": {"id": "1"},
                         "source": {"table": "orders"}}}
    parsed = parse_event(event)
    assert parsed["operation"] == "c"
    assert parsed["table"] == "orders"


def test_malformed_event_is_rejected():
    assert parse_event({"payload": {"op": "x"}}) is None
