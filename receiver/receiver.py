# receiver/receiver.py

from datetime import datetime, timezone
from pydantic import ValidationError

from contracts.receiver_contract import (
    ReceiverInput,
    ReceiverOutput,
    ReceiverFlags,
)
from contracts.common_types import Message, Metadata


def _normalize_timestamp(ts):
    # GUVI sends epoch (ms or sec), contract expects ISO-8601 string
    if isinstance(ts, int):
        # assume milliseconds
        if ts > 10**12:
            ts = ts / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return ts


def handle_receiver(raw_payload: dict) -> ReceiverOutput:
    try:
        # ---- Normalize message ----
        msg = raw_payload.get("message", {})
        normalized_message = Message(
            sender=msg["sender"],
            text=msg["text"],
            timestamp=_normalize_timestamp(msg["timestamp"]),
        )

        # ---- Normalize conversation history ----
        history = []
        for m in raw_payload.get("conversationHistory", []):
            history.append(
                Message(
                    sender=m["sender"],
                    text=m["text"],
                    timestamp=_normalize_timestamp(m["timestamp"]),
                )
            )

        # ---- Normalize metadata ----
        meta = raw_payload.get("metadata", {})
        normalized_metadata = Metadata(
            channel=meta["channel"],
            language=meta["language"],
            locale=meta["locale"],
        )

        flags = ReceiverFlags(
            isFirstMessage=len(history) == 0,
            hasHistory=len(history) > 0,
        )

        return ReceiverOutput(
            sessionId=raw_payload["sessionId"],
            currentMessage=normalized_message,
            history=history,
            metadata=normalized_metadata,
            flags=flags,
        )

    except (KeyError, ValidationError) as e:
        # Let FastAPI convert this to HTTP 400
        raise ValueError(f"Invalid ReceiverInput: {e}")
