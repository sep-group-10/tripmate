import uuid
from datetime import date
from decimal import Decimal

from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant
from app.models.trip import Trip
from app.models.user import User
from app.services.tools.candidate_retriever import retrieve_candidates


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


def test_existing_tourism_records_have_valid_weather_coordinates_and_destinations(
    db_session,
):
    destination_ids = {row[0] for row in db_session.query(Destination.id).all()}

    for model in (Attraction, Hotel, Restaurant, LocalEvent):
        records = db_session.query(model).all()

        assert records, f"Expected seeded {model.__tablename__} records"
        for record in records:
            assert record.latitude is not None
            assert record.longitude is not None
            assert Decimal("-90") <= record.latitude <= Decimal("90")
            assert Decimal("-180") <= record.longitude <= Decimal("180")
            assert record.destination_id is not None
            assert record.destination_id in destination_ids


def test_candidate_retrieval_preserves_destination_and_weather_coordinates(db_session):
    destination_id = _destination_id(db_session, "Kandy")
    candidates = retrieve_candidates(db_session, "Kandy")
    model_category_pairs = (
        (Attraction, "attraction"),
        (Hotel, "hotel"),
        (Restaurant, "restaurant"),
        (LocalEvent, "local_event"),
    )

    assert candidates
    for model, category in model_category_pairs:
        records = (
            db_session.query(model)
            .filter(model.destination_id == destination_id, model.is_active.is_(True))
            .all()
        )
        retrieved = [
            candidate for candidate in candidates if candidate["category"] == category
        ]

        assert records, f"Expected seeded Kandy {model.__tablename__} records"
        assert {candidate["id"] for candidate in retrieved} == {
            str(record.id) for record in records
        }
        for record in records:
            candidate = next(item for item in retrieved if item["id"] == str(record.id))
            assert record.destination_id == destination_id
            assert candidate["latitude"] == float(record.latitude)
            assert candidate["longitude"] == float(record.longitude)


def test_itinerary_day_date_is_retrievable(db_session):
    user = db_session.query(User).filter(User.email == "tourist@demo.com").one()
    trip = Trip(
        user_id=user.id,
        status="draft",
        travel_start_date=date(2026, 10, 5),
        travel_end_date=date(2026, 10, 5),
        duration=1,
        budget=Decimal("1000.00"),
        travel_style="cultural",
        accommodation_preference="hotel",
    )
    db_session.add(trip)
    db_session.flush()

    itinerary = Itinerary(trip_id=trip.id, total_estimated_cost=Decimal("0.00"))
    db_session.add(itinerary)
    db_session.flush()

    itinerary_day = ItineraryDay(
        itinerary_id=itinerary.id,
        day_number=1,
        date=date(2026, 10, 5),
        title="Kandy day one",
    )
    db_session.add(itinerary_day)
    db_session.flush()

    saved_day = (
        db_session.query(ItineraryDay).filter(ItineraryDay.id == itinerary_day.id).one()
    )

    assert saved_day.date == date(2026, 10, 5)
