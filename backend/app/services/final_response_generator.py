"""Build user-facing replies from the final planning state."""

from typing import Any

from app.schemas.agent_session import AgentSession, AgentSessionStatus


def _latest_tool_result(session: AgentSession, tool_name: str) -> dict[str, Any] | None:
    for entry in reversed(session.tool_results):
        if isinstance(entry, dict) and entry.get("tool") == tool_name:
            result = entry.get("result")
            return result if isinstance(result, dict) else None
    return None


def _schedule(session: AgentSession) -> dict[str, Any] | None:
    optimized = _latest_tool_result(session, "route_optimizer")
    if optimized is not None:
        return optimized
    return _latest_tool_result(session, "scheduling_engine")


def _schedule_summary(schedule: dict[str, Any] | None) -> list[str]:
    if schedule is None:
        return []

    days = schedule.get("days")
    if not isinstance(days, list):
        return []

    lines = ["Your itinerary:"]
    for index, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            continue
        day_number = day.get("day_number", index)
        day_date = day.get("date")
        label = f"Day {day_number}"
        if isinstance(day_date, str) and day_date:
            label += f" ({day_date})"

        items = day.get("items")
        names = (
            [
                item["name"]
                for item in items
                if isinstance(item, dict)
                and isinstance(item.get("name"), str)
                and item["name"].strip()
            ]
            if isinstance(items, list)
            else []
        )
        if names:
            lines.append(f"{label}: {', '.join(names)}.")
        else:
            lines.append(f"{label}: no places are scheduled.")
    return lines


def _cost_summary(cost: dict[str, Any] | None) -> str | None:
    if cost is None:
        return None
    total = cost.get("total")
    if not isinstance(total, dict):
        return None
    minimum = total.get("min")
    maximum = total.get("max")
    if minimum is None or maximum is None:
        return None
    if minimum == maximum:
        return f"Estimated total cost: {minimum}."
    return f"Estimated total cost: {minimum}–{maximum}."


def _weather_warnings(weather: dict[str, Any] | None) -> list[str]:
    if weather is None:
        return []
    warnings = weather.get("warnings")
    if not isinstance(warnings, list):
        return []
    return [
        warning.strip()
        for warning in warnings
        if isinstance(warning, str) and warning.strip()
    ]


def _critic_suggestions(session: AgentSession) -> list[str]:
    critic = session.critic_result
    if not isinstance(critic, dict):
        return []
    suggestions = critic.get("suggestions")
    if not isinstance(suggestions, list):
        return []
    return [
        suggestion.strip()
        for suggestion in suggestions
        if isinstance(suggestion, str) and suggestion.strip()
    ]


def _critic_reason(session: AgentSession) -> str | None:
    critic = session.critic_result
    reason = critic.get("reason") if isinstance(critic, dict) else None
    return reason.strip() if isinstance(reason, str) and reason.strip() else None


def _constraint_reasons(session: AgentSession) -> list[str]:
    constraint = session.constraint_result
    reasons = constraint.get("reasons") if isinstance(constraint, dict) else None
    if isinstance(reasons, dict):
        return [
            value.strip()
            for value in reasons.values()
            if isinstance(value, str) and value.strip()
        ]
    return []


def _unscheduled_reasons(schedule: dict[str, Any] | None) -> list[str]:
    unscheduled = schedule.get("unscheduled") if isinstance(schedule, dict) else None
    if not isinstance(unscheduled, list):
        return []
    reasons = []
    for item in unscheduled:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        reason = item.get("reason")
        if isinstance(reason, str) and reason.strip():
            reasons.append(
                f"{name}: {reason}"
                if isinstance(name, str) and name
                else reason.strip()
            )
    return reasons


def _adjustment_suggestions(
    session: AgentSession, schedule: dict[str, Any] | None
) -> list[str]:
    suggestions = _critic_suggestions(session)
    if suggestions:
        return suggestions

    constraint = session.constraint_result
    failed = (
        constraint.get("failed_constraints", []) if isinstance(constraint, dict) else []
    )
    suggestions = []
    if isinstance(failed, list):
        if "budget" in failed:
            suggestions.append("You could raise the budget or reduce trip expenses.")
        if "duration" in failed:
            suggestions.append("You could adjust the travel dates or trip length.")
        if "feasibility" in failed:
            unscheduled = _unscheduled_reasons(schedule)
            if any(
                "date range falls outside the trip" in reason for reason in unscheduled
            ):
                suggestions.append(
                    "You could shift or extend the travel dates to cover the event."
                )
            elif unscheduled:
                suggestions.append(
                    "You could replace or remove activities that could not be scheduled."
                )
    return suggestions


def _supporting_lines(session: AgentSession) -> list[str]:
    lines: list[str] = []
    cost_line = _cost_summary(_latest_tool_result(session, "cost_estimator"))
    if cost_line:
        lines.append(cost_line)
    warnings = _weather_warnings(_latest_tool_result(session, "weather_validator"))
    if warnings:
        lines.append("Weather notes: " + " ".join(warnings))
    return lines


class FinalResponseGenerator:
    """Create a concise response from available planning results."""

    def generate(self, session: AgentSession) -> str:
        status = session.status
        schedule = _schedule(session)
        itinerary_lines = _schedule_summary(schedule)
        critic_reason = _critic_reason(session)
        constraint_reasons = _constraint_reasons(session)
        unscheduled_reasons = _unscheduled_reasons(schedule)

        if status == AgentSessionStatus.COMPLETED:
            lines = ["Your trip plan is ready."]
            lines.extend(itinerary_lines)
            lines.extend(_supporting_lines(session))
            return "\n".join(lines)

        if status == AgentSessionStatus.BEST_EFFORT:
            lines = [
                "Here is a best-effort trip plan. It may be incomplete or imperfect."
            ]
            lines.extend(itinerary_lines)
            if critic_reason:
                lines.append(critic_reason)
            lines.extend(
                f"Planning limitation: {reason}" for reason in constraint_reasons
            )
            lines.extend(f"Not scheduled: {reason}" for reason in unscheduled_reasons)
            lines.extend(_supporting_lines(session))
            suggestions = _adjustment_suggestions(session, schedule)
            if suggestions:
                lines.append("You could adjust: " + " ".join(suggestions))
            return "\n".join(lines)

        if status == AgentSessionStatus.INFEASIBLE:
            lines = ["I couldn't find a trip plan that satisfies the request."]
            if critic_reason:
                lines.append(critic_reason)
            lines.extend(constraint_reasons)
            lines.extend(
                f"Scheduling issue: {reason}" for reason in unscheduled_reasons
            )
            schedule_warnings = (
                schedule.get("warnings") if isinstance(schedule, dict) else None
            )
            if isinstance(schedule_warnings, list):
                lines.extend(
                    f"Scheduling note: {warning}"
                    for warning in schedule_warnings
                    if isinstance(warning, str) and warning.strip()
                )
            lines.extend(_supporting_lines(session))
            suggestions = _adjustment_suggestions(session, schedule)
            if suggestions:
                lines.append("You could consider: " + " ".join(suggestions))
            return "\n".join(lines)

        # Failed responses intentionally do not include tool results, Critic
        # details, or exception text.
        return "I’m sorry, but I couldn’t complete your trip plan. Please try again or adjust your trip details."
