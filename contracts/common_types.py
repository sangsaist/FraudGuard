from enum import Enum
from typing import Literal
from pydantic import BaseModel


class Message(BaseModel):
    sender: Literal["scammer", "user"]
    text: str
    timestamp: str  # ISO-8601


class Metadata(BaseModel):
    channel: str
    language: str
    locale: str


class ResponseStyle(str, Enum):
    NAIVE = "NAIVE"
    CONFUSED = "CONFUSED"
    HESITANT = "HESITANT"
    URGENT = "URGENT"
    NEUTRAL = "NEUTRAL"
