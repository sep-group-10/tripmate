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
    for candidate in candidates:
        assert set(candidate.keys()) == {
            "id",
            "category",
            "name",
            "description",
            "rating",
        }
        assert isinstance(candidate["id"], str)
