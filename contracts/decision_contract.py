from pydantic import BaseModel
from typing import List, Optional
from contracts.common_types import Message, Metadata, ResponseStyle


# ======================
# Intelligence
# ======================
class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str]
    upiIds: List[str]
    phishingLinks: List[str]
    phoneNumbers: List[str]
    suspiciousKeywords: List[str]


# ======================
# Session Stats
# ======================
class SessionStats(BaseModel):
    totalMessages: int
    scammerMessages: int
    agentMessages: int
    noNewIntelligenceTurns: int


# ======================
# Flags
# ======================
class DecisionFlags(BaseModel):
    isFirstMessage: bool
    hasHistory: bool


# ======================
# Decision Input
# ======================
class DecisionInput(BaseModel):
    sessionId: str
    currentState: str              # 🔑 ADDED
    currentMessage: Message
    history: List[Message]
    metadata: Metadata
    extractedIntelligence: ExtractedIntelligence
    sessionStats: SessionStats
    flags: DecisionFlags


# ======================
# Agent Control
# ======================
class NextAgentAction(BaseModel):
    shouldReply: bool
    responseStyle: ResponseStyle


# ======================
# Decision Output
# ======================
class DecisionOutput(BaseModel):
    scamDetected: bool
    scamType: Optional[str]
    continueConversation: bool
    triggerFinalCallback: bool
    agentNotes: str

    nextState: str                 # 🔑 ADDED (SOURCE OF TRUTH)

    nextAgentAction: NextAgentAction
