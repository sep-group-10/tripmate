import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ItineraryEditPlan(BaseModel):
    """A proposed itinerary edit; describing an edit never applies it."""

    operation: Literal["remove", "add", "replace", "move", "change"]
    target_item: str | None = Field(
        default=None,
        description="Name or persisted itinerary item ID of the item being edited.",
    )
    source_day: int | None = Field(default=None, ge=1)
    destination_day: int | None = Field(default=None, ge=1)
    destination_time: str | None = Field(
        default=None, description="Requested local time or time of day."
    )
    replacement_item: str | None = None
    requested_change: str | None = Field(
        default=None,
        description="Requested change or preference, such as a cheaper activity.",
    )


class PlannerDecision(BaseModel):
    action: Literal[
        "candidate_retriever",
        "scoring_engine",
        "scheduling_engine",
        "route_optimizer",
        "weather_validator",
        "cost_estimator",
        "constraint_validator",
    ]
    edit_plan: ItineraryEditPlan | None = Field(
        default=None,
        description="Proposed edit for the current itinerary, or null when none.",
    )


class CriterionAssessment(BaseModel):
    score: int = Field(ge=1, le=5, strict=True)
    reasoning: str = Field(min_length=1)

    @field_validator("reasoning")
    @classmethod
    def require_one_sentence(cls, value: str) -> str:
        text = value.strip()
        endings = []
        for match in re.finditer(r"[.!?](?=\s|$)", text):
            punctuation = match.group()
            if punctuation == ".":
                prefix = text[: match.start()]
                if re.search(r"\d$", prefix) and re.match(r"\d", text[match.end() :]):
                    continue
                if re.search(
                    r"(?i)(?:\b(?:e\.g|i\.e|etc|vs|mr|mrs|ms|dr|prof|sr|jr|st)|"
                    r"(?:[a-z]\.){2,})\.$",
                    text[: match.end()],
                ):
                    continue
            endings.append(match)
        if len(endings) != 1 or not re.search(r"[.!?][\"')\]]?$", text):
            raise ValueError("reasoning must contain exactly one sentence")
        return text


class CriticDecision(BaseModel):
    # Tells the graph whether planning should continue.
    continue_planning: bool

    # The final status when the planning process should stop.
    status: Literal["completed", "best_effort", "infeasible", "failed"] | None = None

    # Optional general explanation accompanying the structured quality review.
    reason: str | None = None

    variety: CriterionAssessment
    daily_balance: CriterionAssessment
    interest_match: CriterionAssessment
    pacing: CriterionAssessment
    suggestions: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("suggestions")
    @classmethod
    def require_nonempty_suggestions(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("suggestions must be non-empty strings")
        return values
