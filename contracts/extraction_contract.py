from pydantic import BaseModel
from typing import List, Literal


class ExtractionInput(BaseModel):
    sessionId: str
    messageText: str
    sender: Literal["scammer", "user"]
    timestamp: str  # ISO-8601


class ExtractionIntelligence(BaseModel):
    bankAccounts: List[str]
    upiIds: List[str]
    phishingLinks: List[str]
    phoneNumbers: List[str]
    suspiciousKeywords: List[str]


class ExtractionOutput(BaseModel):
    sessionId: str
    intelligence: ExtractionIntelligence
    deltaDetected: bool
