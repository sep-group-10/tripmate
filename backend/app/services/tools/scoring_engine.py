"""Scoring engine tool for the TripMate planning graph."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from langchain_core.tools import tool

from app.services.opening_hours import parse_opening_hours


@dataclass
class ScoringWeights:
    """Configurable weights for combining scoring factors into a final score."""

    semantic: float = 0.45
    rating: float = 0.25
    budget_fit: float = 0.20
    availability: float = 0.10


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _semantic_score(candidate: dict[str, Any]) -> float:
    score = candidate.get("similarity_score")
    return 1.0 if score is None else _to_float(score)


def _rating_score(candidate: dict[str, Any]) -> float:
    rating_value = _to_float(candidate.get("rating"))
    rating = 3.0 if rating_value is None else rating_value
    return rating / 5.0


def _budget_score(candidate: dict[str, Any], preferences: dict[str, Any]) -> float:
    entry_fee = _to_float(candidate.get("entry_fee"))
    if entry_fee is None:
        return 1.0

    budget = _to_float(preferences.get("budget"))
    duration_days = preferences.get("duration_days")
    travelers = preferences.get("travelers")

    if not budget or not duration_days or not travelers:
        return 1.0

    daily_per_person = budget / duration_days / travelers
    if daily_per_person <= 0:
        return 1.0

    return max(0.0, 1.0 - (entry_fee / daily_per_person))


def _trip_days(preferences: dict[str, Any]) -> list[date]:
    start_date = preferences.get("start_date")
    end_date = preferences.get("end_date")

    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return []
    if end_date < start_date:
        return []

    days = []
    current = start_date
    while current <= end_date:
        days.append(current)
        current += timedelta(days=1)
    return days


def _availability_score(
    candidate: dict[str, Any], preferences: dict[str, Any]
) -> float:
    opening_hours = candidate.get("opening_hours")
    if not isinstance(opening_hours, dict):
        return 0.5

    trip_days = _trip_days(preferences)
    if not trip_days:
        return 0.5

    parsed_hours = parse_opening_hours(opening_hours)
    is_open_any_day = any(not parsed_hours.for_date(day).is_closed for day in trip_days)
    return 1.0 if is_open_any_day else 0.0


def score_candidates(
    candidates: list[dict[str, Any]],
    preferences: dict[str, Any],
    weights: ScoringWeights | None = None,
) -> list[dict[str, Any]]:
    """Score and rank candidates by how well they match trip preferences."""

    if weights is None:
        weights = ScoringWeights()

    scored: list[dict[str, Any]] = []

    for candidate in candidates:
        semantic = _semantic_score(candidate)
        rating = _rating_score(candidate)
        budget_fit = _budget_score(candidate, preferences)
        availability = _availability_score(candidate, preferences)

        final_score = (
            semantic * weights.semantic
            + rating * weights.rating
            + budget_fit * weights.budget_fit
            + availability * weights.availability
        )

        scored.append(
            {
                **candidate,
                "final_score": final_score,
                "score_breakdown": {
                    "semantic": semantic,
                    "rating": rating,
                    "budget_fit": budget_fit,
                    "availability": availability,
                },
            }
        )

    scored.sort(key=lambda candidate: candidate["final_score"], reverse=True)
    return scored


@tool
def scoring_engine(candidates: list[dict], preferences: dict) -> list[dict]:
    """Ranks tourism candidates by how well they match trip preferences.

    Uses rating, budget fit, availability, and semantic similarity score.
    """
    return score_candidates(candidates, preferences)
