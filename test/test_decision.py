import pytest

from decision.decision import decide
from contracts.decision_contract import DecisionInput
from contracts.common_types import Message, Metadata
from contracts.decision_contract import (
    ExtractedIntelligence,
    SessionStats,
    DecisionFlags,
)


def _base_input(
    text: str,
    extracted: ExtractedIntelligence,
    total_messages: int = 1,
):
    return DecisionInput(
        sessionId="sess-1",
        currentMessage=Message(
            sender="scammer",
            text=text,
            timestamp="2026-01-01T10:00:00Z",
        ),
        history=[],
        metadata=Metadata(
            channel="SMS",
            language="en",
            locale="IN",
        ),
        extractedIntelligence=extracted,
        sessionStats=SessionStats(
            totalMessages=total_messages,
            scammerMessages=total_messages,
            agentMessages=0,
        ),
        flags=DecisionFlags(
            isFirstMessage=total_messages == 1,
            hasHistory=total_messages > 1,
        ),
    )


def test_non_scam_message():
    # Arrange
    input_data = _base_input(
        text="Hello, how are you?",
        extracted=ExtractedIntelligence(
            bankAccounts=[],
            upiIds=[],
            phishingLinks=[],
            phoneNumbers=[],
            suspiciousKeywords=[],
        ),
    )

    # Act
    output = decide(input_data)

    # Assert (SOFT_EXIT recommendation)
    assert output.scamDetected is False
    assert output.nextAgentAction.shouldReply is False
    assert output.triggerFinalCallback is False
    assert output.continueConversation is False


def test_initial_scam_signal():
    # Arrange
    input_data = _base_input(
        text="Your account is blocked, verify immediately",
        extracted=ExtractedIntelligence(
            bankAccounts=[],
            upiIds=[],
            phishingLinks=[],
            phoneNumbers=[],
            suspiciousKeywords=[],
        ),
    )

    # Act
    output = decide(input_data)

    # Assert (SUSPECTED_SCAM recommendation)
    assert output.scamDetected is False
    assert output.nextAgentAction.shouldReply is True
    assert output.nextAgentAction.responseStyle.name in {"NAIVE", "CONFUSED"}
    assert output.triggerFinalCallback is False
    assert output.continueConversation is True


def test_confirmed_scam():
    # Arrange
    input_data = _base_input(
        text="Pay via UPI now or account will be suspended",
        extracted=ExtractedIntelligence(
            bankAccounts=[],
            upiIds=["scammer@upi"],
            phishingLinks=[],
            phoneNumbers=[],
            suspiciousKeywords=["upi"],
        ),
    )

    # Act
    output = decide(input_data)

    # Assert (ENGAGING recommendation)
    assert output.scamDetected is True
    assert output.nextAgentAction.shouldReply is True
    assert output.continueConversation is True
    assert output.triggerFinalCallback is False


def test_intelligence_saturation():
    # Arrange
    input_data = _base_input(
        text="Send money now",
        extracted=ExtractedIntelligence(
            bankAccounts=["123456789"],
            upiIds=["scammer@upi"],
            phishingLinks=["http://phish.test"],
            phoneNumbers=["9999999999"],
            suspiciousKeywords=["urgent"],
        ),
        total_messages=5,
    )

    # Act
    output = decide(input_data)

    # Assert (INTELLIGENCE_SATURATED recommendation)
    assert output.scamDetected is True
    assert output.continueConversation is False
    assert output.nextAgentAction.responseStyle.name == "NEUTRAL"


def test_callback_readiness():
    # Arrange
    input_data = _base_input(
        text="Final reminder: pay now",
        extracted=ExtractedIntelligence(
            bankAccounts=["123456789"],
            upiIds=["scammer@upi"],
            phishingLinks=["http://phish.test"],
            phoneNumbers=["9999999999"],
            suspiciousKeywords=["urgent"],
        ),
        total_messages=6,
    )

    # Act
    output = decide(input_data)

    # Assert (CALLBACK readiness recommendation)
    assert output.scamDetected is True
    assert output.triggerFinalCallback is True
    assert output.continueConversation is False
