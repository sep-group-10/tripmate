import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class PlannerDecision(BaseModel):
    action: str
    arguments: dict[str, Any] = Field(default_factory=dict)


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
