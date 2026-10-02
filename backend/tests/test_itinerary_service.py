from datetime import date, time
from decimal import Decimal

import pytest

from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.itinerary_day_item import ItineraryDayItem
from app.models.trip import Trip
from app.models.user import User
from app.schemas.chat import ChatItinerary
from app.services.itinerary_service import persist_chat_itinerary


def _trip(db_session):
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
    return trip


def _itinerary(end_time="11:30"):
    return ChatItinerary.model_validate(
        {
            "status": "completed",
            "days": [
                {
                    "day_number": 1,
                    "date": "2026-10-05",
                    "day_type": "full",
                    "items": [
                        {
                            "candidate_id": "place-1",
                            "category": "attraction",
                            "name": "Temple visit",
                            "start_time": "09:00",
                            "end_time": end_time,
                        }
                    ],
                    "warnings": [],
                }
            ],
            "hotel_by_destination": {},
            "unscheduled": [],
            "warnings": [],
        }
    )


def test_persist_chat_itinerary_maps_rows_and_cost(db_session):
    trip = _trip(db_session)

    persisted = persist_chat_itinerary(
        db_session,
        trip.id,
        _itinerary(),
        {"total": {"min": 100, "max": 200}},
    )

    day = db_session.query(ItineraryDay).filter_by(itinerary_id=persisted.id).one()
    item = db_session.query(ItineraryDayItem).filter_by(itinerary_day_id=day.id).one()
    assert persisted.total_estimated_cost == Decimal("150.00")
    assert day.day_number == 1
    assert day.date == date(2026, 10, 5)
    assert day.title == "full"
    assert item.item_type == "attraction"
    assert item.title == "Temple visit"
    assert item.start_time == time(9, 0)
    assert item.end_time == time(11, 30)
    assert item.sort_order == 0
    assert trip.status == "generated"
    assert persisted.created_at is not None


def test_missing_cost_does_not_use_trip_budget(db_session):
    trip = _trip(db_session)
    persisted = persist_chat_itinerary(db_session, trip.id, _itinerary())

    assert persisted.total_estimated_cost == Decimal("0.00")
    assert persisted.total_estimated_cost != trip.budget


def test_failed_persistence_rolls_back_all_itinerary_rows(db_session):
    trip = _trip(db_session)

    with pytest.raises(ValueError):
        persist_chat_itinerary(
            db_session,
            trip.id,
            _itinerary(end_time="not-a-time"),
            {"total": {"min": 100, "max": 200}},
        )

    assert db_session.query(Itinerary).filter_by(trip_id=trip.id).count() == 0
    assert trip.status == "draft"
