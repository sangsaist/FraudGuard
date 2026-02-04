from pydantic import BaseModel
from typing import List
from contracts.common_types import Message, Metadata


class ReceiverInput(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message]
    metadata: Metadata


class ReceiverFlags(BaseModel):
    isFirstMessage: bool
    hasHistory: bool


class ReceiverOutput(BaseModel):
    sessionId: str
    currentMessage: Message
    history: List[Message]
    metadata: Metadata
    flags: ReceiverFlags
