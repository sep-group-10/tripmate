import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.schemas.preference import PreferenceResult
from app.services.chat_response_generator import ChatResponseGenerator


class FakeChatModel:
    """Return a fixed response and record prompts without calling Gemini."""

    def __init__(self, response):
        self.response = AIMessage(content=response)
        self.calls = []

    def invoke(self, messages):
        self.calls.append(list(messages))
        return self.response


def _generator_with_response(
    response: str,
) -> tuple[ChatResponseGenerator, FakeChatModel]:
    generator = ChatResponseGenerator.__new__(ChatResponseGenerator)
    model = FakeChatModel(response)
    generator.model = model
    return generator, model


def test_generate_natural_reply_for_normal_conversation():
    generator, model = _generator_with_response("Hello! What can I help you plan?")
    conversation = [HumanMessage(content="Hello there")]

    response = generator.generate(
        conversation,
        PreferenceResult(intent="normal_conversation"),
    )

    assert response == "Hello! What can I help you plan?"
    assert model.calls[0][0].type == "system"
    assert model.calls[0][1] == conversation[0]
    assert "Respond naturally" in model.calls[0][0].content


def test_generate_extracts_text_blocks_from_list_content():
    generator, model = _generator_with_response(
        [
            {"type": "text", "text": "  When would you like "},
            {"type": "text", "text": "to travel?  "},
        ]
    )

    response = generator.generate(
        [HumanMessage(content="I want to visit Kandy")],
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            missing_fields=["dates"],
        ),
    )

    assert response == "When would you like to travel?"
    assert len(model.calls) == 1


def test_generate_follow_up_using_only_missing_fields():
    generator, model = _generator_with_response("When would you like to travel?")
    conversation = [HumanMessage(content="I want to visit Kandy")]
    preferences = PreferenceResult(
        intent="trip_planning",
        destination="Kandy",
        missing_fields=["dates", "budget"],
    )

    response = generator.generate(conversation, preferences)

    assert response == "When would you like to travel?"
    prompt = model.calls[0]
    assert prompt[1] == conversation[0]
    assert "dates, budget" in prompt[0].content
    assert "do not ask about any other trip preference" in prompt[0].content
    assert "Do not claim that planning has started" in prompt[0].content


def test_generate_rejects_content_without_usable_text():
    generator, _ = _generator_with_response([{"type": "image", "url": "image"}])

    with pytest.raises(TypeError, match="no usable text"):
        generator.generate(
            [HumanMessage(content="Hello")],
            PreferenceResult(intent="normal_conversation"),
        )


def test_complete_trip_preferences_do_not_generate_missing_field_question():
    generator, model = _generator_with_response("This should not be used")
    preferences = PreferenceResult(
        intent="trip_planning",
        destination="Kandy",
        missing_fields=[],
    )

    response = generator.generate([], preferences)

    assert response is None
    assert model.calls == []
