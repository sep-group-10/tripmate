from langchain_core.messages import HumanMessage

from app.schemas.langgraph import GeminiResponse
from app.services.langgraph.gemini_graph import gemini_graph


def test_langgraph_calls_gemini():
    result = gemini_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Reply with exactly: LangGraph Gemini works."
                )
            ]
        }
    )

    assert result["structured_response"]
    assert isinstance(result["structured_response"], GeminiResponse)


def test_gemini_can_call_tool():
    result = gemini_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Use the get_tripmate_status tool to check the "
                        "TripMate integration status, then provide the "
                        "result in your final response."
                    )
                )
            ]
        }
    )

    structured_response = result["structured_response"]

    assert isinstance(structured_response, GeminiResponse)
    assert structured_response.status
    assert structured_response.message
    assert "TripMate LangGraph integration is working." in (
        structured_response.message
    )