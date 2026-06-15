from app.logging_config import scrub_event
from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_supported_pii_patterns() -> None:
    text = (
        "Phone 090 123 4567, CCCD 012345678901, card 4111-1111-1111-1111, "
        "passport B1234567; Địa chỉ: 12 Nguyễn Trãi, Phường 7, Quận 5"
    )

    out = scrub_text(text)

    assert "090 123 4567" not in out
    assert "012345678901" not in out
    assert "4111-1111-1111-1111" not in out
    assert "B1234567" not in out
    assert "12 Nguyễn Trãi" not in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "REDACTED_PASSPORT" in out
    assert "REDACTED_ADDRESS_VN" in out


def test_scrub_does_not_treat_correlation_id_as_passport() -> None:
    assert scrub_text("req-e3606108") == "req-e3606108"


def test_scrub_event_handles_nested_payloads() -> None:
    event = {
        "event": "Contact student@vinuni.edu.vn",
        "payload": {
            "contacts": ["090 123 4567", {"card": "4111 1111 1111 1111"}],
        },
    }

    scrubbed = scrub_event(None, "info", event)

    assert "student@" not in scrubbed["event"]
    assert scrubbed["payload"]["contacts"][0] == "[REDACTED_PHONE_VN]"
    assert scrubbed["payload"]["contacts"][1]["card"] == "[REDACTED_CREDIT_CARD]"
