from typing import List

from groq import Groq

from contracts.agent_contract import AgentInput, AgentOutput
from contracts.common_types import ResponseStyle
from app.config import GROQ_API_KEY


def _build_system_prompt(style: ResponseStyle, language: str, locale: str) -> str:
    if style == ResponseStyle.NAIVE:
        return (
            "You are a normal person chatting online. "
            "You sound curious, trusting, and a little unaware. "
            "Ask simple clarification questions. "
            "Do not accuse or warn anyone. "
            "Do not mention scams, safety, or systems."
        )

    if style == ResponseStyle.CONFUSED:
        return (
            "You are a normal person who is confused and slightly worried. "
            "You do not fully understand what is being asked. "
            "Ask for clarification in a hesitant way. "
            "Do not accuse or warn anyone. "
            "Do not mention scams, safety, or systems."
        )

    if style == ResponseStyle.HESITANT:
        return (
            "You are a cautious person. "
            "You respond slowly and carefully. "
            "You avoid sharing details and ask indirect questions. "
            "Do not accuse or warn anyone. "
            "Do not mention scams, safety, or systems."
        )

    # NEUTRAL (soft exit)
    return (
        "You are a polite person disengaging from the conversation. "
        "Keep the response short and neutral. "
        "Do not ask questions. "
        "Do not accuse or warn anyone. "
        "Do not mention scams, safety, or systems."
    )


def _build_conversation(history: List, current_message) -> List[dict]:
    messages: List[dict] = []

    for msg in history:
        role = "assistant" if msg.sender == "user" else "user"
        messages.append(
            {
                "role": role,
                "content": msg.text,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": current_message.text,
        }
    )

    return messages


def generate_reply(agent_input: AgentInput) -> AgentOutput:
    # ======================
    # API Key from config.py
    # ======================
    if not GROQ_API_KEY:
        return AgentOutput(
            status="fail",
            reply="",
        )

    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = _build_system_prompt(
        agent_input.responseStyle,
        agent_input.metadata.language,
        agent_input.metadata.locale,
    )

    conversation = _build_conversation(
        agent_input.history,
        agent_input.currentMessage,
    )

    messages = [{"role": "system", "content": system_prompt}] + conversation

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.6,
            max_tokens=120,
        )

        reply_text = completion.choices[0].message.content.strip()

        if not reply_text:
            return AgentOutput(
                status="fail",
                reply="",
            )

        return AgentOutput(
            status="success",
            reply=reply_text,
        )

    except Exception:
        return AgentOutput(
            status="fail",
            reply="",
        )
