import pytest

from extraction.extraction import extract
from contracts.extraction_contract import ExtractionInput


def test_upi_extraction():
    input_data = ExtractionInput(
        sessionId="sess-1",
        messageText="Please send money to testuser@upi",
        sender="scammer",
        timestamp="2026-01-01T10:00:00Z",
    )

    output = extract(input_data)

    assert "testuser@upi" in output.intelligence.upiIds
    assert output.deltaDetected is True


def test_uppercase_upi_extraction():
    input_data = ExtractionInput(
        sessionId="sess-2",
        messageText="Transfer amount to SECURE@UPI immediately",
        sender="scammer",
        timestamp="2026-01-01T10:01:00Z",
    )

    output = extract(input_data)

    assert "SECURE@UPI" in output.intelligence.upiIds
    assert output.deltaDetected is True


def test_phone_number_extraction():
    input_data = ExtractionInput(
        sessionId="sess-3",
        messageText="Call me at 9876543210 immediately",
        sender="scammer",
        timestamp="2026-01-01T10:02:00Z",
    )

    output = extract(input_data)

    assert "9876543210" in output.intelligence.phoneNumbers
    assert output.deltaDetected is True


def test_url_extraction():
    input_data = ExtractionInput(
        sessionId="sess-4",
        messageText="Verify your account here: https://phish.example.com",
        sender="scammer",
        timestamp="2026-01-01T10:03:00Z",
    )

    output = extract(input_data)

    assert "https://phish.example.com" in output.intelligence.phishingLinks
    assert output.deltaDetected is True


def test_suspicious_keyword_extraction():
    input_data = ExtractionInput(
        sessionId="sess-5",
        messageText="Your account is blocked, verify urgently",
        sender="scammer",
        timestamp="2026-01-01T10:04:00Z",
    )

    output = extract(input_data)

    assert "blocked" in output.intelligence.suspiciousKeywords
    assert "urgent" in output.intelligence.suspiciousKeywords
    assert output.deltaDetected is True


def test_no_intelligence_found():
    input_data = ExtractionInput(
        sessionId="sess-6",
        messageText="Hello, how are you doing today?",
        sender="user",
        timestamp="2026-01-01T10:05:00Z",
    )

    output = extract(input_data)

    assert output.intelligence.upiIds == []
    assert output.intelligence.phoneNumbers == []
    assert output.intelligence.phishingLinks == []
    assert output.intelligence.suspiciousKeywords == []
    assert output.deltaDetected is False


def test_duplicate_intelligence_no_delta():
    input_data = ExtractionInput(
        sessionId="sess-7",
        messageText="Okay noted, thanks.",
        sender="scammer",
        timestamp="2026-01-01T10:06:00Z",
    )

    output = extract(input_data)

    assert output.intelligence.upiIds == []
    assert output.intelligence.phoneNumbers == []
    assert output.intelligence.phishingLinks == []
    assert output.intelligence.suspiciousKeywords == []
    assert output.deltaDetected is False
