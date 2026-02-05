import os
import requests
from typing import Set
from contracts.callback_contract import CallbackPayload

ENV = os.getenv("ENV", "local")

CALLBACK_URLS = {
    "local": "http://127.0.0.1:9000/api/updateHoneyPotFinalResult",
    "guvi": "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
}

GUVI_CALLBACK_URL = CALLBACK_URLS.get(ENV, CALLBACK_URLS["local"])

REQUEST_TIMEOUT_SECONDS = 5
_SENT_SESSIONS: Set[str] = set()


def send_callback(payload: CallbackPayload) -> bool:
    if not payload.scamDetected:
        return False

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
            print(f"[CALLBACK ERROR] {response.status_code}")
            return False

        _SENT_SESSIONS.add(payload.sessionId)
        print(f"[CALLBACK SUCCESS] ENV={ENV}")
        return True

    except requests.RequestException as e:
        print(f"[CALLBACK EXCEPTION] {e}")
        return False
