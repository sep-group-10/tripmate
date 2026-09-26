from collections.abc import Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.preference import PreferenceResult


class PreferenceProcessor:
    """Extract structured trip preferences from conversation history."""

    def __init__(self) -> None:
        self.model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0,
        ).with_structured_output(PreferenceResult)

    def process(self, messages: Sequence[BaseMessage]) -> PreferenceResult:
        """Process conversation messages and return structured preferences."""

        conversation = "\n".join(
            f"{message.type}: {message.content}" for message in messages
        )

        prompt = [
            SystemMessage(
                content=(
                    "You are TripMate's preference extraction assistant. "
                    "Analyze the complete conversation and extract trip "
                    "preferences into the required structured schema.\n\n"
                    "Classify the conversation as either "
                    "'trip_planning' or 'normal_conversation'.\n\n"
                    "For trip planning requests, extract every preference "
                    "that is explicitly stated. Do not invent missing "
                    "information.\n\n"
                    "For trip-planning conversations, missing_fields may "
                    "contain only these logical names: destination, dates, "
                    "duration_days, budget, travelers, interests, and "
                    "transport_type. "
                    "When travel dates are missing, use dates. Never use "
                    "start_date or end_date in missing_fields.\n\n"
                    "Extract transport_type only when the user explicitly "
                    "states their preferred transport type. For trip-planning "
                    "conversations, include transport_type in missing_fields "
                    "when the user has not provided it. Do not infer or "
                    "invent a transport type.\n\n"
                    "For normal conversation, set intent to "
                    "'normal_conversation' and keep missing_fields empty. "
                    "Do not mark trip fields as missing for normal "
                    "conversation."
                )
            ),
            HumanMessage(content=conversation),
        ]

        result = self.model.invoke(prompt)

        if not isinstance(result, PreferenceResult):
            raise TypeError("Gemini returned an invalid preference result")

        return result
