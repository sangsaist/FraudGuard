from pydantic import BaseModel
from typing import List, Optional
from contracts.common_types import Message, Metadata, ResponseStyle


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str]
    upiIds: List[str]
    phishingLinks: List[str]
    phoneNumbers: List[str]
    suspiciousKeywords: List[str]


class SessionStats(BaseModel):
    totalMessages: int
    scammerMessages: int
    agentMessages: int


class DecisionFlags(BaseModel):
    isFirstMessage: bool
    hasHistory: bool


class DecisionInput(BaseModel):
    sessionId: str
    currentMessage: Message
    history: List[Message]
    metadata: Metadata
    extractedIntelligence: ExtractedIntelligence
    sessionStats: SessionStats
    flags: DecisionFlags


class NextAgentAction(BaseModel):
    shouldReply: bool
    responseStyle: ResponseStyle


class DecisionOutput(BaseModel):
    scamDetected: bool
    scamType: Optional[str]
    continueConversation: bool
    triggerFinalCallback: bool
    agentNotes: str
    nextAgentAction: NextAgentAction
