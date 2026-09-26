import uuid
from datetime import date
from decimal import Decimal

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


def test_attraction_duration_not_null_after_migration(db_session):
    attractions = db_session.query(Attraction).all()

    assert len(attractions) > 0
    assert all(attraction.duration_hours is not None for attraction in attractions)


def test_event_starts_on_ends_on_exist_and_are_dates(db_session):
    events = db_session.query(LocalEvent).all()

    assert len(events) > 0
    for event in events:
        assert isinstance(event.starts_on, date)
        assert isinstance(event.ends_on, date)
        # Existing seed events are single-day.
        assert event.starts_on == event.ends_on


def test_event_supports_multiday_range(db_session):
    kandy_id = _destination_id(db_session, "Kandy")

    multiday_event = LocalEvent(
        id=uuid.uuid4(),
        destination_id=kandy_id,
        name="Kandy Esala Perahera",
        description="A multi-day cultural procession.",
        latitude=Decimal("7.2906"),
        longitude=Decimal("80.6337"),
        rating=Decimal("4.9"),
        entry_fee=Decimal("0.00"),
        event_schedule={
            "date": "2026-08-10",
            "start_time": "18:00",
            "end_time": "22:00",
        },
        starts_on=date(2026, 8, 10),
        ends_on=date(2026, 8, 20),
        is_active=True,
    )
    db_session.add(multiday_event)
    db_session.flush()

    saved = (
        db_session.query(LocalEvent).filter(LocalEvent.id == multiday_event.id).one()
    )

    assert saved.starts_on == date(2026, 8, 10)
    assert saved.ends_on == date(2026, 8, 20)
    assert saved.starts_on != saved.ends_on
