from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.preferences import TripPreferences


def create_preference_model():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    ).with_structured_output(TripPreferences)


def process_preferences(
    messages: list[BaseMessage],
) -> TripPreferences:
    """Extract structured trip preferences from conversation messages."""

    conversation = "\n".join(
        f"{message.type}: {message.content}" for message in messages
    )

    prompt = f"""
You are the TripMate PreferenceProcessor.

Read the conversation below and extract the user's trip preferences.

Conversation:
{conversation}

Extract these fields:
- destination
- dates
- budget
- travelers
- interests

Rules:
- Only extract information that is actually present in the conversation.
- Do not invent or guess missing information.
- If a field is not available, leave it empty.
- Return only the structured TripPreferences response.
"""

    model = create_preference_model()
    result = model.invoke(prompt)

    missing_fields = []

    if result.destination is None:
        missing_fields.append("destination")

    if result.dates is None:
        missing_fields.append("dates")

    if result.budget is None:
        missing_fields.append("budget")

    if result.travelers is None:
        missing_fields.append("travelers")

    if not result.interests:
        missing_fields.append("interests")

    result.missing_fields = missing_fields

    return result
