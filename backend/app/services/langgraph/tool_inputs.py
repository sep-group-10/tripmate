from app.services.tools.registry import TOOLS


def _latest_tool_result(session, tool_name: str):
    return next(
        (
            entry["result"]
            for entry in reversed(session.tool_results)
            if entry.get("tool") == tool_name
        ),
        None,
    )


def _assemble_tool_input(session, tool_name: str) -> dict | None:
    """Build registered tool inputs from canonical requirements and stored outputs."""

    requirements = session.trip_requirements
    if tool_name == "candidate_retriever":
        destination = requirements.get("destination")
        return {"destination": destination} if destination is not None else None
    if tool_name == "scoring_engine":
        candidates = _latest_tool_result(session, "candidate_retriever")
        if candidates is None:
            return None
        return {"candidates": candidates, "preferences": requirements}
    if tool_name == "scheduling_engine":
        candidates = _latest_tool_result(session, "scoring_engine")
        if candidates is None:
            return None
        return {"candidates": candidates, "trip_requirements": requirements}
    if tool_name == "route_optimizer":
        schedule = _latest_tool_result(session, "route_optimizer")
        if schedule is None:
            schedule = _latest_tool_result(session, "scheduling_engine")
        return {"schedule": schedule} if schedule is not None else None
    if tool_name == "weather_validator":
        # Keep weather validation tied to the scheduling result, as before.
        schedule = _latest_tool_result(session, "scheduling_engine")
        return {"schedule": schedule} if schedule is not None else None
    if tool_name == "cost_estimator":
        itinerary = _latest_tool_result(session, "route_optimizer")
        if itinerary is None:
            itinerary = _latest_tool_result(session, "scheduling_engine")
        candidates = _latest_tool_result(session, "scoring_engine")
        if candidates is None:
            candidates = _latest_tool_result(session, "candidate_retriever")
        if itinerary is None or candidates is None:
            return None
        return {
            "itinerary": itinerary,
            "candidates": candidates,
            "trip_requirements": requirements,
        }
    if tool_name == "constraint_validator":
        itinerary = _latest_tool_result(session, "route_optimizer")
        if itinerary is None:
            itinerary = _latest_tool_result(session, "scheduling_engine")
        cost_estimate = _latest_tool_result(session, "cost_estimator")
        if itinerary is None or cost_estimate is None:
            return None
        return {
            "itinerary": itinerary,
            "trip_requirements": requirements,
            "cost_estimate": cost_estimate,
        }
    return None


def runnable_tool_names(session, *, allow_replanning: bool = False) -> list[str]:
    """Return available tools, excluding completed stages outside replanning."""

    candidates = _latest_tool_result(session, "candidate_retriever")
    scored = _latest_tool_result(session, "scoring_engine")
    scheduled = _latest_tool_result(session, "scheduling_engine")

    # Before advancing to a downstream stage, expose only that stage's next tool.
    if candidates is not None and scored is None:
        return ["scoring_engine"]
    if scored is not None and scheduled is None:
        return ["scheduling_engine"]

    available = [
        name
        for name in TOOLS
        if name != "constraint_validator"
        and _assemble_tool_input(session, name) is not None
    ]
    if allow_replanning:
        return available

    completed = {
        entry.get("tool")
        for entry in session.tool_results
        if isinstance(entry, dict) and entry.get("result") is not None
    }
    return [name for name in available if name not in completed]
