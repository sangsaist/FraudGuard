from typing import Dict

from receiver.receiver import handle_receiver
from decision.decision import decide
from aiagent.agent import generate_reply
from extraction.extraction import extract
from callback.callback import send_callback

from contracts.decision_contract import DecisionInput, DecisionFlags, SessionStats
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


# ======================
# Session Store
# ======================
_SESSION_STORE: Dict[str, Dict] = {}


def _init_session() -> Dict:
    return {
        "runtimeState": NEW_MESSAGE,
        "totalMessages": 0,
        "scammerMessages": 0,
        "agentMessages": 0,
        "noNewIntelligenceTurns": 0,
        "extractedIntelligence": {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
        },
        "callbackSent": False,
    }


def _merge_intelligence(existing: Dict, new: Dict) -> bool:
    before = sum(len(v) for v in existing.values())
    for k in existing:
        existing[k] = list(set(existing[k] + new.get(k, [])))
    after = sum(len(v) for v in existing.values())
    return after > before


# ======================
# Entry
# ======================
def handle_request(raw_payload: dict) -> dict:
    receiver_output = handle_receiver(raw_payload)
    session_id = receiver_output.sessionId

    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = _init_session()

    session = _SESSION_STORE[session_id]

    decision_input = DecisionInput(
        sessionId=session_id,
        currentState=session["runtimeState"],
        currentMessage=receiver_output.currentMessage,
        history=receiver_output.history,
        metadata=receiver_output.metadata,
        extractedIntelligence=session["extractedIntelligence"],
        sessionStats=SessionStats(
            totalMessages=session["totalMessages"],
            scammerMessages=session["scammerMessages"],
            agentMessages=session["agentMessages"],
            noNewIntelligenceTurns=session["noNewIntelligenceTurns"],
        ),
        flags=DecisionFlags(
            isFirstMessage=receiver_output.flags.isFirstMessage,
            hasHistory=receiver_output.flags.hasHistory,
        ),
    )

    decision_output = decide(decision_input)

    # 🔑 SINGLE SOURCE OF TRUTH
    session["runtimeState"] = decision_output.nextState

    agent_output = None

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
        session["agentMessages"] += 1

    if session["runtimeState"] in {SUSPECTED_SCAM, ENGAGING}:
        extraction_output = extract(
            ExtractionInput(
                sessionId=session_id,
                messageText=receiver_output.currentMessage.text,
                sender=receiver_output.currentMessage.sender,
                timestamp=receiver_output.currentMessage.timestamp,
            )
        )
        delta = _merge_intelligence(
            session["extractedIntelligence"],
            extraction_output.intelligence.model_dump(),
        )
        session["noNewIntelligenceTurns"] = 0 if delta else session["noNewIntelligenceTurns"] + 1

    session["totalMessages"] += 1
    if receiver_output.currentMessage.sender == "scammer":
        session["scammerMessages"] += 1

    if (
        session["runtimeState"] == CALLBACK_READY
        and not session["callbackSent"]
    ):
        send_callback(
            CallbackPayload(
                sessionId=session_id,
                scamDetected=True,
                totalMessagesExchanged=session["totalMessages"],
                extractedIntelligence=session["extractedIntelligence"],
                agentNotes=decision_output.agentNotes,
            )
        )
        session["callbackSent"] = True
        session["runtimeState"] = CLOSED

    if agent_output:
        return agent_output.model_dump()

    return {"status": "success", "reply": ""}
