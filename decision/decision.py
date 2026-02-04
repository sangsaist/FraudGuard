from typing import List

from contracts.decision_contract import (
    DecisionInput,
    DecisionOutput,
    NextAgentAction,
)
from contracts.common_types import ResponseStyle


SCAM_KEYWORDS: List[str] = [
    "urgent",
    "verify",
    "account",
    "blocked",
    "suspended",
    "otp",
    "upi",
    "click",
    "link",
    "immediately",
    "payment",
    "bank",
]


SATURATION_MESSAGE_THRESHOLD = 3


def _contains_scam_signals(text: str) -> bool:
    lowered = text.lower()

    strong_keywords = {"otp", "verify", "blocked", "click", "link"}
    weak_keywords = {"bank", "account", "payment"}

    strong_hits = sum(1 for kw in strong_keywords if kw in lowered)
    weak_hits = sum(1 for kw in weak_keywords if kw in lowered)

    return strong_hits >= 1 or weak_hits >= 2


def _intelligence_present(extracted) -> bool:
    return any(
        [
            extracted.bankAccounts,
            extracted.upiIds,
            extracted.phishingLinks,
            extracted.phoneNumbers,
        ]
    )


def decide(input_data: DecisionInput) -> DecisionOutput:
    message_text = input_data.currentMessage.text

    scam_signals = _contains_scam_signals(message_text)
    intelligence_found = _intelligence_present(input_data.extractedIntelligence)

    scam_detected = intelligence_found

    continue_conversation = False
    trigger_final_callback = False
    should_reply = False
    response_style = ResponseStyle.NEUTRAL
    scam_type = None
    agent_notes = ""

    if not scam_signals and not intelligence_found:
        should_reply = False
        continue_conversation = False
        agent_notes = "No scam indicators detected."

    elif scam_signals and not intelligence_found:
        should_reply = True
        continue_conversation = True
        response_style = ResponseStyle.CONFUSED
        agent_notes = "Suspicious patterns detected in message."

    elif intelligence_found:
        scam_type = "financial_scam"
        should_reply = True
        continue_conversation = True
        response_style = ResponseStyle.HESITANT
        agent_notes = "Scam confirmed via extracted intelligence."

        if input_data.sessionStats.totalMessages > SATURATION_MESSAGE_THRESHOLD:
            should_reply = False
            continue_conversation = False
            trigger_final_callback = True
            response_style = ResponseStyle.NEUTRAL
            agent_notes = "Intelligence saturation reached."

    return DecisionOutput(
        scamDetected=scam_detected,
        scamType=scam_type,
        continueConversation=continue_conversation,
        triggerFinalCallback=trigger_final_callback,
        agentNotes=agent_notes,
        nextAgentAction=NextAgentAction(
            shouldReply=should_reply,
            responseStyle=response_style,
        ),
    )
