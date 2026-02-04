from pydantic import BaseModel
from typing import List, Literal
from contracts.common_types import Message, Metadata, ResponseStyle


class AgentConstraints(BaseModel):
    noAccusation: bool
    noIllegalAdvice: bool
    softTone: bool


class AgentInput(BaseModel):
    sessionId: str
    currentMessage: Message
    history: List[Message]
    metadata: Metadata
    responseStyle: ResponseStyle
    constraints: AgentConstraints


class AgentOutput(BaseModel):
    status: Literal["success", "fail"]
    reply: str
