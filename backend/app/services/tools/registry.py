from langchain_core.tools import BaseTool, tool


@tool
def placeholder_tool() -> str:
    """Provide a temporary result until the real TripMate tools are implemented."""
    return "Placeholder tool executed successfully."


TOOLS: dict[str, BaseTool] = {
    "placeholder_tool": placeholder_tool,
}
