from langchain_core.tools import BaseTool, tool

from app.services.tools.candidate_retriever import candidate_retriever


@tool
def placeholder_tool() -> str:
    """Provide a temporary result until the real TripMate tools are implemented."""
    return "Placeholder tool executed successfully."


TOOLS: dict[str, BaseTool] = {
    "placeholder_tool": placeholder_tool,
    "candidate_retriever": candidate_retriever,
}
