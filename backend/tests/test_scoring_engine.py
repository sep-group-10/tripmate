from datetime import date
from decimal import Decimal

from app.services.tools.scoring_engine import ScoringWeights, score_candidates

BASE_PREFERENCES = {
    "budget": Decimal("500"),
    "duration_days": 3,
    "travelers": 2,
    "start_date": date(2026, 10, 5),
    "end_date": date(2026, 10, 7),
}


def _candidate(**overrides):
    base = {
        "id": "c1",
        "name": "Test Place",
        "description": "A test place",
        "rating": Decimal("4.0"),
        "entry_fee": Decimal("10.00"),
        "similarity_score": 1.0,
        "opening_hours": {
            "monday": "08:00-18:00",
            "tuesday": "08:00-18:00",
            "wednesday": "08:00-18:00",
            "thursday": "08:00-18:00",
            "friday": "08:00-18:00",
            "saturday": "08:00-18:00",
            "sunday": "08:00-18:00",
        },
    }
    base.update(overrides)
    return base


def test_higher_rated_place_ranks_above_lower_rated():
    candidates = [
        _candidate(id="low", rating=Decimal("2.0")),
        _candidate(id="high", rating=Decimal("4.8")),
    ]

    result = score_candidates(candidates, BASE_PREFERENCES)

    assert [c["id"] for c in result] == ["high", "low"]


def test_cheap_entry_fee_ranks_above_expensive():
    candidates = [
        _candidate(id="expensive", entry_fee=Decimal("400.00")),
        _candidate(id="cheap", entry_fee=Decimal("1.00")),
    ]

    result = score_candidates(candidates, BASE_PREFERENCES)

    assert [c["id"] for c in result] == ["cheap", "expensive"]


def test_open_on_trip_days_ranks_above_closed():
    closed_hours = {
        "monday": "08:00-18:00",
        "tuesday": "08:00-18:00",
        "wednesday": "08:00-18:00",
        "thursday": "08:00-18:00",
        "friday": "08:00-18:00",
        "saturday": "08:00-18:00",
        "sunday": "08:00-18:00",
    }
    # Trip is Oct 5-7 2026 (Mon-Wed); make "closed" candidate closed on those days
    closed_hours = {
        day: hours
        for day, hours in closed_hours.items()
        if day not in ("monday", "tuesday", "wednesday")
    }

    candidates = [
        _candidate(id="closed", opening_hours=closed_hours),
        _candidate(id="open"),
    ]

    result = score_candidates(candidates, BASE_PREFERENCES)

    assert [c["id"] for c in result] == ["open", "closed"]


def test_missing_similarity_score_falls_back_to_neutral():
    candidate = _candidate()
    del candidate["similarity_score"]

    result = score_candidates([candidate], BASE_PREFERENCES)

    assert result[0]["score_breakdown"]["semantic"] == 1.0


def test_missing_rating_falls_back_to_industry_average():
    candidate = _candidate()
    del candidate["rating"]

    result = score_candidates([candidate], BASE_PREFERENCES)

    assert result[0]["score_breakdown"]["rating"] == 3.0 / 5.0


def test_missing_entry_fee_falls_back_to_free():
    candidate = _candidate()
    del candidate["entry_fee"]

    result = score_candidates([candidate], BASE_PREFERENCES)

    assert result[0]["score_breakdown"]["budget_fit"] == 1.0


def test_unknown_opening_hours_falls_back_to_half():
    candidate = _candidate()
    del candidate["opening_hours"]

    result = score_candidates([candidate], BASE_PREFERENCES)

    assert result[0]["score_breakdown"]["availability"] == 0.5


def test_different_weights_produce_different_rankings():
    candidates = [
        _candidate(
            id="high_rating_expensive",
            rating=Decimal("5.0"),
            entry_fee=Decimal("450.00"),
        ),
        _candidate(
            id="low_rating_cheap", rating=Decimal("2.0"), entry_fee=Decimal("1.00")
        ),
    ]

    rating_heavy = ScoringWeights(
        semantic=0.0, rating=1.0, budget_fit=0.0, availability=0.0
    )
    budget_heavy = ScoringWeights(
        semantic=0.0, rating=0.0, budget_fit=1.0, availability=0.0
    )

    rating_ranked = score_candidates(candidates, BASE_PREFERENCES, weights=rating_heavy)
    budget_ranked = score_candidates(candidates, BASE_PREFERENCES, weights=budget_heavy)

    assert [c["id"] for c in rating_ranked] == [
        "high_rating_expensive",
        "low_rating_cheap",
    ]
    assert [c["id"] for c in budget_ranked] == [
        "low_rating_cheap",
        "high_rating_expensive",
    ]


def test_empty_candidate_list_returns_empty_list():
    assert score_candidates([], BASE_PREFERENCES) == []


def test_result_is_sorted_descending_by_final_score():
    candidates = [
        _candidate(id="a", rating=Decimal("3.0")),
        _candidate(id="b", rating=Decimal("5.0")),
        _candidate(id="c", rating=Decimal("1.0")),
    ]

    result = score_candidates(candidates, BASE_PREFERENCES)

    scores = [c["final_score"] for c in result]
    assert scores == sorted(scores, reverse=True)
