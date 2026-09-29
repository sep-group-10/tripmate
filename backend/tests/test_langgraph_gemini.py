"""Deterministic tests for the small Gemini/LangGraph example integration."""

from langchain_core.messages import AIMessage, HumanMessage

from app.schemas.langgraph import GeminiResponse
from app.services.langgraph import gemini_graph as gemini_graph_module


class FakeModel:
    def __init__(self, responses):
        self.responses = iter(responses)

    def invoke(self, messages):
        return next(self.responses)


class FakeStructuredModel:
    def __init__(self, result):
        self.result = result
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return self.result


def test_langgraph_returns_deterministic_structured_response(monkeypatch):
    structured_model = FakeStructuredModel(
        GeminiResponse(status="ok", message="LangGraph Gemini works.")
    )
    monkeypatch.setattr(
        gemini_graph_module,
        "get_model",
        lambda: FakeModel([AIMessage(content="Ready.")]),
    )
    monkeypatch.setattr(
        gemini_graph_module, "get_structured_model", lambda: structured_model
    )

    result = gemini_graph_module.gemini_graph.invoke(
        {"messages": [HumanMessage(content="Reply with a greeting.")]}
    )

    assert isinstance(result["structured_response"], GeminiResponse)
    assert result["structured_response"].message == "LangGraph Gemini works."
    assert "human: Reply with a greeting." in structured_model.prompts[0]


def test_langgraph_tool_call_is_stubbed_and_included_in_final_context(monkeypatch):
    structured_model = FakeStructuredModel(
        GeminiResponse(
            status="ok",
            message="TripMate LangGraph integration is working.",
        )
    )
    model = FakeModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_tripmate_status",
                        "args": {},
                        "id": "call-status-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="The status tool succeeded."),
        ]
    )
    monkeypatch.setattr(gemini_graph_module, "get_model", lambda: model)
    monkeypatch.setattr(
        gemini_graph_module, "get_structured_model", lambda: structured_model
    )

    result = gemini_graph_module.gemini_graph.invoke(
        {"messages": [HumanMessage(content="Check the integration status.")]}
    )

    assert isinstance(result["structured_response"], GeminiResponse)
    assert result["structured_response"].message == (
        "TripMate LangGraph integration is working."
    )
    prompt = structured_model.prompts[0]
    assert "TripMate LangGraph integration is working." in prompt
    assert "Check the integration status." in prompt
