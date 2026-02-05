# callback/callback.py

import requests
from typing import Set

from contracts.callback_contract import CallbackPayload


GUVI_CALLBACK_URL = "http://127.0.0.1:9000/api/updateHoneyPotFinalResult"

REQUEST_TIMEOUT_SECONDS = 5

# In-memory idempotency guard (session-scoped, process lifetime)
_SENT_SESSIONS: Set[str] = set()


def send_callback(payload: CallbackPayload) -> bool:
    # Do not send callback for non-scam sessions
    if payload.scamDetected is False:
        return False

    # Idempotency: ensure callback is sent exactly once per session
    if payload.sessionId in _SENT_SESSIONS:
        return False

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload.model_dump(),
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            return False

        _SENT_SESSIONS.add(payload.sessionId)
        return True

    except requests.RequestException:
        return False
