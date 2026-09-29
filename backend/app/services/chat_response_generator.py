from collections.abc import Sequence

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.preference import PreferenceResult


class ChatResponseGenerator:
    """Generate a user-facing reply for normal chat or missing preferences."""

    def __init__(self) -> None:
        self.model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0,
        )

    def generate(
        self,
        messages: Sequence[BaseMessage],
        preferences: PreferenceResult,
    ) -> str | None:
        """Generate a reply, or return None when planning is ready to start."""
        if preferences.intent == "normal_conversation":
            instructions = (
                "You are TripMate, a helpful travel assistant. Respond naturally "
                "to the user's latest message using the conversation for context. "
                "Do not assume they are asking to plan a trip unless they say so."
            )
        elif preferences.missing_fields:
            fields = ", ".join(preferences.missing_fields)
            instructions = (
                "You are TripMate, a helpful travel assistant. Ask the user a "
                "natural, concise follow-up to collect these missing trip "
                f"preferences: {fields}. These are the authoritative fields to "
                "ask about: do not ask about any other trip preference, even if "
                "other information is absent from the conversation. Do not claim "
                "that planning has started. Use the conversation for context "
                "and avoid asking for information the user already provided."
            )
        else:
            return None

        response = self.model.invoke([SystemMessage(content=instructions), *messages])
        content = response.content
        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            text = "".join(
                block["text"]
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "text"
                and isinstance(block.get("text"), str)
            ).strip()
        else:
            text = ""

        if not text:
            raise TypeError("Gemini returned no usable text in the chat response")
        return text
