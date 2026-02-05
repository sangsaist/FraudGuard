from typing import List
from contracts.decision_contract import (
    DecisionInput,
    DecisionOutput,
    NextAgentAction,
)
from contracts.common_types import ResponseStyle


# ======================
# Scam signal keywords
# ======================
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

# Number of turns with no new intelligence before saturation
SATURATION_LIMIT = 3


# ======================
# Helpers
# ======================
def _contains_scam_signals(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in SCAM_KEYWORDS)


def _intelligence_present(intel) -> bool:
    return any([
        intel.bankAccounts,
        intel.upiIds,
        intel.phishingLinks,
        intel.phoneNumbers,
    ])


# ======================
# Decision Logic
# ======================
def decide(input_data: DecisionInput) -> DecisionOutput:
    state = input_data.currentState
    text = input_data.currentMessage.text

    scam_signals = _contains_scam_signals(text)
    intelligence_found = _intelligence_present(input_data.extractedIntelligence)

    # ----------------------
    # Defaults (safe)
    # ----------------------
    next_state = state
    should_reply = False
    response_style = ResponseStyle.NEUTRAL
    continue_conversation = False
    trigger_callback = False
    scam_detected = False
    scam_type = None
    agent_notes = ""

    # ======================
    # NEW_MESSAGE
    # ======================
    if state == "NEW_MESSAGE":
        if scam_signals:
            next_state = "SUSPECTED_SCAM"
            should_reply = True
            continue_conversation = True
            response_style = ResponseStyle.CONFUSED
            agent_notes = "Initial scam indicators detected."
        else:
            next_state = "SOFT_EXIT"
            agent_notes = "No scam indicators."

    # ======================
    # SUSPECTED_SCAM
    # ======================
    elif state == "SUSPECTED_SCAM":
        if intelligence_found:
            next_state = "ENGAGING"
            should_reply = True
            continue_conversation = True
            response_style = ResponseStyle.HESITANT
            agent_notes = "Scam confirmed, entering engagement."
        elif scam_signals:
            next_state = "SUSPECTED_SCAM"
            should_reply = True
            continue_conversation = True
            response_style = ResponseStyle.CONFUSED
            agent_notes = "Suspicion reinforced."
        else:
            next_state = "SOFT_EXIT"
            agent_notes = "Suspicion dropped."

    # ======================
    # ENGAGING
    # ======================
    elif state == "ENGAGING":
        if input_data.sessionStats.noNewIntelligenceTurns >= SATURATION_LIMIT:
            next_state = "INTELLIGENCE_SATURATED"
            agent_notes = "Intelligence saturation reached."
        else:
            next_state = "ENGAGING"
            should_reply = True
            continue_conversation = True
            response_style = ResponseStyle.HESITANT
            agent_notes = "Actively engaging to extract intelligence."

    # ======================
    # INTELLIGENCE_SATURATED
    # ======================
    elif state == "INTELLIGENCE_SATURATED":
        next_state = "SOFT_EXIT"
        should_reply = True
        response_style = ResponseStyle.NEUTRAL
        agent_notes = "Neutral disengagement message sent."

    # ======================
    # SOFT_EXIT
    # ======================
    elif state == "SOFT_EXIT":
        if intelligence_found:
            next_state = "CALLBACK_READY"
            scam_detected = True
            scam_type = "financial_scam"
            trigger_callback = True
            agent_notes = "Conversation complete, ready for callback."
        else:
            next_state = "CLOSED"
            agent_notes = "Non-scam conversation closed."

    # ======================
    # CALLBACK_READY
    # ======================
    elif state == "CALLBACK_READY":
        next_state = "CLOSED"
        scam_detected = True
        trigger_callback = True
        agent_notes = "Callback finalized."

    # ======================
    # CLOSED
    # ======================
    elif state == "CLOSED":
        next_state = "CLOSED"

    return DecisionOutput(
        scamDetected=scam_detected,
        scamType=scam_type,
        continueConversation=continue_conversation,
        triggerFinalCallback=trigger_callback,
        agentNotes=agent_notes,
        nextState=next_state,
        nextAgentAction=NextAgentAction(
            shouldReply=should_reply,
            responseStyle=response_style,
        ),
    )
