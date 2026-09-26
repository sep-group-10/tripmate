from app.models.attraction import Attraction
from app.models.restaurant import Restaurant
from app.services.tools.candidate_retriever import retrieve_candidates


def test_retrieve_candidates_returns_matches_for_known_destination(db_session):
    candidates = retrieve_candidates(db_session, "Kandy")

    assert len(candidates) > 0
    categories = {candidate["category"] for candidate in candidates}
    assert categories == {"attraction", "restaurant", "local_event", "hotel"}


def test_retrieve_candidates_only_returns_matching_destination(db_session):
    kandy_candidates = retrieve_candidates(db_session, "Kandy")
    galle_candidates = retrieve_candidates(db_session, "Galle")

    kandy_names = {candidate["name"] for candidate in kandy_candidates}
    galle_names = {candidate["name"] for candidate in galle_candidates}

    assert kandy_names.isdisjoint(galle_names)


def test_retrieve_candidates_returns_empty_list_for_unknown_destination(db_session):
    candidates = retrieve_candidates(db_session, "Nonexistent City")

    assert candidates == []


def test_retrieve_candidates_returns_empty_list_when_destination_missing(db_session):
    assert retrieve_candidates(db_session, None) == []
    assert retrieve_candidates(db_session, "") == []


def test_retrieve_candidates_result_shape(db_session):
    candidates = retrieve_candidates(db_session, "Colombo")

    assert len(candidates) > 0
    expected_keys = {
        "id",
        "category",
        "name",
        "description",
        "rating",
        "entry_fee",
        "opening_hours",
        "duration_minutes",
        "latitude",
        "longitude",
        "starts_on",
        "ends_on",
        "event_start_time",
        "event_end_time",
        "similarity_score",
    }
    for candidate in candidates:
        assert set(candidate.keys()) == expected_keys
        assert isinstance(candidate["id"], str)


def test_restaurant_candidate_dict_has_normalized_fields(db_session):
    """Restaurant rows use avg_meal_cost and operating_hours.

    CandidateRetriever must normalize these to entry_fee and opening_hours
    so ScoringEngine receives a consistent dict shape.
    """
    candidates = retrieve_candidates(db_session, "Kandy")
    restaurants = [c for c in candidates if c["category"] == "restaurant"]

    assert len(restaurants) > 0
    for restaurant in restaurants:
        assert "entry_fee" in restaurant
        assert "opening_hours" in restaurant
        assert "avg_meal_cost" not in restaurant
        assert "operating_hours" not in restaurant

    matching_row = (
        db_session.query(Restaurant)
        .filter(Restaurant.name == restaurants[0]["name"])
        .one()
    )
    assert restaurants[0]["entry_fee"] == matching_row.avg_meal_cost
    assert restaurants[0]["opening_hours"] == matching_row.operating_hours


def test_attraction_duration_minutes_is_integer(db_session):
    candidates = retrieve_candidates(db_session, "Kandy")
    attractions = [c for c in candidates if c["category"] == "attraction"]

    assert len(attractions) > 0
    matching_row = (
        db_session.query(Attraction)
        .filter(Attraction.name == attractions[0]["name"])
        .one()
    )

    assert isinstance(attractions[0]["duration_minutes"], int)
    assert attractions[0]["duration_minutes"] == int(matching_row.duration_hours * 60)


def test_event_candidate_dict_has_date_fields(db_session):
    candidates = retrieve_candidates(db_session, "Kandy")
    events = [c for c in candidates if c["category"] == "local_event"]

    assert len(events) > 0
    for event in events:
        assert event["starts_on"] is not None
        assert event["ends_on"] is not None
        assert "event_start_time" in event
        assert "event_end_time" in event


def test_hotel_candidate_dict_duration_is_none(db_session):
    candidates = retrieve_candidates(db_session, "Kandy")
    hotels = [c for c in candidates if c["category"] == "hotel"]

    assert len(hotels) > 0
    for hotel in hotels:
        assert hotel["duration_minutes"] is None
        assert hotel["opening_hours"] is None


def test_serializers_return_consistent_keys(db_session):
    candidates = retrieve_candidates(db_session, "Kandy")

    assert len(candidates) > 0
    key_sets = {frozenset(candidate.keys()) for candidate in candidates}
    assert len(key_sets) == 1
