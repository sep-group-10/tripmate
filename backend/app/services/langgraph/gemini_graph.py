# This graph verifies the Gemini integration with LangGraph,
# including Gemini tool calling and structured responses.
# The main TripMate planning workflow is implemented separately
# in planning_graph.py.
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.schemas.langgraph import GeminiResponse


@tool
def get_tripmate_status() -> str:
    """Return the current status of the TripMate assistant."""
    return "TripMate LangGraph integration is working."


class GeminiState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    structured_response: GeminiResponse


def get_model():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    ).bind_tools([get_tripmate_status])


def get_structured_model():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    ).with_structured_output(GeminiResponse)


tool_node = ToolNode([get_tripmate_status])


def call_gemini(state: GeminiState) -> dict:
    model = get_model()
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def create_structured_response(state: GeminiState) -> dict:
    # Gemini 3.6 Flash does not support model-prefill.
    # Send the conversation as context inside a new user message instead.
    structured_model = get_structured_model()

    conversation = "\n".join(
        f"{message.type}: {message.content}" for message in state["messages"]
    )

    prompt = f"""
Create the final TripMate response based on the conversation below.

Conversation:
{conversation}

Return a structured response with:
- status: a short status value
- message: the final response for the user
"""

    response = structured_model.invoke(prompt)

    return {
        "structured_response": response,
    }


def route_after_gemini(state: GeminiState) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "structured"


graph_builder = StateGraph(GeminiState)

graph_builder.add_node("gemini", call_gemini)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("structured", create_structured_response)

graph_builder.add_edge(START, "gemini")

graph_builder.add_conditional_edges(
    "gemini",
    route_after_gemini,
    {
        "tools": "tools",
        "structured": "structured",
    },
)

graph_builder.add_edge("tools", "gemini")
graph_builder.add_edge("structured", END)

gemini_graph = graph_builder.compile()
