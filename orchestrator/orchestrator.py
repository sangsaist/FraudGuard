# orchestrator/orchestrator.py

from typing import Dict

from receiver.receiver import handle_receiver
from decision.decision import decide
from aiagent.agent import generate_reply
from extraction.extraction import extract
from callback.callback import send_callback

from contracts.decision_contract import DecisionInput, DecisionFlags
from contracts.agent_contract import AgentInput
from contracts.callback_contract import CallbackPayload
from contracts.extraction_contract import ExtractionInput


# ======================
# Runtime States
# ======================
NEW_MESSAGE = "NEW_MESSAGE"
SUSPECTED_SCAM = "SUSPECTED_SCAM"
ENGAGING = "ENGAGING"
INTELLIGENCE_SATURATED = "INTELLIGENCE_SATURATED"
SOFT_EXIT = "SOFT_EXIT"
CALLBACK_READY = "CALLBACK_READY"
CLOSED = "CLOSED"

VALID_STATES = {
    NEW_MESSAGE,
    SUSPECTED_SCAM,
    ENGAGING,
    INTELLIGENCE_SATURATED,
    SOFT_EXIT,
    CALLBACK_READY,
    CLOSED,
}


# ======================
# Session Store
# ======================
_SESSION_STORE: Dict[str, Dict] = {}


def _init_session() -> Dict:
    return {
        "runtimeState": NEW_MESSAGE,
        "messageCount": 0,
        "extractedIntelligence": {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
        },
        "callbackSent": False,
    }


def _merge_intelligence(existing: Dict, new: Dict) -> Dict:
    return {
        k: list(set(existing[k] + new.get(k, [])))
        for k in existing
    }


def _next_state(current_state: str, decision_output) -> str:
    if current_state == NEW_MESSAGE:
        return SUSPECTED_SCAM if decision_output.continueConversation else SOFT_EXIT
    if current_state == SUSPECTED_SCAM:
        return ENGAGING if decision_output.continueConversation else SOFT_EXIT
    if current_state == ENGAGING:
        return (
            INTELLIGENCE_SATURATED
            if not decision_output.continueConversation
            else ENGAGING
        )
    if current_state == INTELLIGENCE_SATURATED:
        return SOFT_EXIT
    if current_state == SOFT_EXIT:
        return CALLBACK_READY if decision_output.scamDetected else CLOSED
    if current_state == CALLBACK_READY:
        return CLOSED
    return CLOSED


# ======================
# Orchestrator Entry
# ======================
def handle_request(raw_payload: dict) -> dict:
    # Step 1–2: Receiver
    receiver_output = handle_receiver(raw_payload)
    session_id = receiver_output.sessionId

    # ======================
    # EARLY EXIT (Benign First Message)
    # ======================
    if (
        receiver_output.currentMessage.sender == "user"
        and receiver_output.flags.isFirstMessage
    ):
        if session_id not in _SESSION_STORE:
            _SESSION_STORE[session_id] = _init_session()
        return {"status": "success", "reply": ""}

    # Step 3: Load session
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = _init_session()

    session = _SESSION_STORE[session_id]

    # Step 4: Decision Input
    decision_input = DecisionInput(
        sessionId=session_id,
        currentMessage=receiver_output.currentMessage,
        history=receiver_output.history,
        metadata=receiver_output.metadata,
        extractedIntelligence=session["extractedIntelligence"],
        sessionStats={
            "totalMessages": session["messageCount"],
            "scammerMessages": session["messageCount"],
            "agentMessages": 0,
        },
        flags=DecisionFlags(
            isFirstMessage=receiver_output.flags.isFirstMessage,
            hasHistory=receiver_output.flags.hasHistory,
        ),
    )

    # Step 5: Decision
    decision_output = decide(decision_input)

    # Step 6: State transition
    proposed = _next_state(session["runtimeState"], decision_output)
    session["runtimeState"] = proposed if proposed in VALID_STATES else CLOSED

    agent_output = None

    # Step 7: Agent
    if decision_output.nextAgentAction.shouldReply:
        agent_output = generate_reply(
            AgentInput(
                sessionId=session_id,
                currentMessage=receiver_output.currentMessage,
                history=receiver_output.history,
                metadata=receiver_output.metadata,
                responseStyle=decision_output.nextAgentAction.responseStyle,
                constraints={
                    "noAccusation": True,
                    "noIllegalAdvice": True,
                    "softTone": True,
                },
            )
        )

    # Step 8: Extraction
    if agent_output or receiver_output.currentMessage.sender == "scammer":
        extraction_output = extract(
            ExtractionInput(
                sessionId=session_id,
                messageText=receiver_output.currentMessage.text,
                sender=receiver_output.currentMessage.sender,
                timestamp=receiver_output.currentMessage.timestamp,
            )
        )
        session["extractedIntelligence"] = _merge_intelligence(
            session["extractedIntelligence"],
            extraction_output.intelligence.model_dump(),
        )

    # Step 9: Update counters
    session["messageCount"] += 1

    # Step 10: Callback (FINAL & IDENTITY-SAFE)
    if (
        decision_output.scamDetected
        and not decision_output.continueConversation
        and not session["callbackSent"]
    ):
        if send_callback(
            CallbackPayload(
                sessionId=session_id,
                scamDetected=True,
                totalMessagesExchanged=session["messageCount"],
                extractedIntelligence=session["extractedIntelligence"],
                agentNotes=decision_output.agentNotes,
            )
        ):
            session["callbackSent"] = True
            session["runtimeState"] = CLOSED

    # Step 11: API response
    if agent_output:
        if hasattr(agent_output, "model_dump"):
            return agent_output.model_dump()
        return agent_output

    return {"status": "success", "reply": ""}
