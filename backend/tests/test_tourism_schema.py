from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant


def _destination_id(db_session, name):
    return db_session.query(Destination.id).filter(Destination.name == name).scalar()


def test_query_attractions_by_destination_returns_only_that_destinations_records(
    db_session,
):
    kandy_id = _destination_id(db_session, "Kandy")
    galle_id = _destination_id(db_session, "Galle")

    attractions = (
        db_session.query(Attraction).filter(Attraction.destination_id == kandy_id).all()
    )

    assert len(attractions) > 0
    assert all(attraction.destination_id == kandy_id for attraction in attractions)
    assert all(attraction.destination_id != galle_id for attraction in attractions)


def test_inactive_record_excluded_when_filtering_by_is_active(db_session):
    kandy_id = _destination_id(db_session, "Kandy")

    active_attraction = (
        db_session.query(Attraction)
        .filter(Attraction.destination_id == kandy_id)
        .first()
    )
    active_attraction.is_active = False
    db_session.flush()

    results = (
        db_session.query(Attraction)
        .filter(
            Attraction.destination_id == kandy_id,
            Attraction.is_active.is_(True),
        )
        .all()
    )

    assert active_attraction.id not in {row.id for row in results}


def test_query_across_all_four_tables_by_destination_returns_correct_rows(db_session):
    kandy_id = _destination_id(db_session, "Kandy")
    galle_id = _destination_id(db_session, "Galle")

    for model in (Attraction, Hotel, Restaurant, LocalEvent):
        kandy_rows = (
            db_session.query(model).filter(model.destination_id == kandy_id).all()
        )
        galle_rows = (
            db_session.query(model).filter(model.destination_id == galle_id).all()
        )

        assert len(kandy_rows) > 0
        assert len(galle_rows) > 0
        assert all(row.destination_id == kandy_id for row in kandy_rows)
        assert all(row.destination_id == galle_id for row in galle_rows)
