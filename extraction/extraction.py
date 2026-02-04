# extraction/extraction.py

import re
from typing import List

from contracts.extraction_contract import (
    ExtractionInput,
    ExtractionOutput,
    ExtractionIntelligence,
)


# ---------- Regex Patterns (Deterministic) ----------

UPI_REGEX = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+91[-\s]?|0)?[6-9]\d{9}\b")
URL_REGEX = re.compile(r"https?://[^\s]+")

SUSPICIOUS_KEYWORDS = [
    "urgent",
    "verify",
    "blocked",
    "suspended",
    "otp",
    "payment",
    "bank",
    "account",
    "click",
    "immediately",
]


def _extract_upi(text: str) -> List[str]:
    return list(set(UPI_REGEX.findall(text)))


def _extract_phones(text: str) -> List[str]:
    return list(set(PHONE_REGEX.findall(text)))


def _extract_urls(text: str) -> List[str]:
    return list(set(URL_REGEX.findall(text)))


def _extract_keywords(text: str) -> List[str]:
    lowered = text.lower()
    return [kw for kw in SUSPICIOUS_KEYWORDS if kw in lowered]


def extract(input_data: ExtractionInput) -> ExtractionOutput:
    text = input_data.messageText

    upi_ids = _extract_upi(text)
    phone_numbers = _extract_phones(text)
    phishing_links = _extract_urls(text)
    suspicious_keywords = _extract_keywords(text)

    delta_detected = any(
        [
            upi_ids,
            phone_numbers,
            phishing_links,
            suspicious_keywords,
        ]
    )

    intelligence = ExtractionIntelligence(
        bankAccounts=[],
        upiIds=upi_ids,
        phishingLinks=phishing_links,
        phoneNumbers=phone_numbers,
        suspiciousKeywords=suspicious_keywords,
    )

    return ExtractionOutput(
        sessionId=input_data.sessionId,
        intelligence=intelligence,
        deltaDetected=delta_detected,
    )
