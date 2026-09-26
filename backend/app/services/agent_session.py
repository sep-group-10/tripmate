"""Factories for initializing planning agent sessions."""

from app.schemas.agent_session import AgentSession
from app.schemas.preference import PreferenceResult


def create_agent_session(trip_preferences: PreferenceResult) -> AgentSession:
    """Create a planning session from complete trip preferences."""

    if trip_preferences.intent != "trip_planning":
        raise ValueError("Agent sessions require trip planning preferences")

    if trip_preferences.missing_fields:
        raise ValueError("Agent sessions require complete trip preferences")

    trip_requirements = {
        "destination": trip_preferences.destination,
        "start_date": trip_preferences.start_date,
        "end_date": trip_preferences.end_date,
        "duration_days": trip_preferences.duration_days,
        "budget": trip_preferences.budget,
        "travelers": trip_preferences.travelers,
        "interests": list(trip_preferences.interests),
        "transport_type": trip_preferences.transport_type,
    }
    goal = (
        f"Plan a trip to {trip_preferences.destination}"
        if trip_preferences.destination
        else "Plan a trip"
    )

    return AgentSession(goal=goal, trip_requirements=trip_requirements)
