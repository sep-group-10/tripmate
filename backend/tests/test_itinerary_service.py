from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timezone
from decimal import Decimal
from threading import Barrier, Lock
from time import sleep

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.itinerary_day_item import ItineraryDayItem
from app.models.trip import Trip
from app.models.user import User
from app.schemas.chat import ChatItinerary
from app.services.itinerary_service import (
    _latest_itinerary,
    persist_chat_itinerary,
    persist_removed_chat_item,
)


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
    assert persisted.revision_number == 1


def test_revisions_increment_and_legacy_rows_remain_unordered(db_session):
    trip = _trip(db_session)
    legacy = Itinerary(
        trip_id=trip.id,
        total_estimated_cost=Decimal("0.00"),
        revision_number=None,
    )
    db_session.add(legacy)
    db_session.flush()

    first = persist_chat_itinerary(db_session, trip.id, _itinerary())
    second = persist_chat_itinerary(db_session, trip.id, _itinerary())

    assert first.revision_number == 1
    assert second.revision_number == 2
    assert _latest_itinerary(db_session, trip.id).id == second.id
    assert db_session.get(Itinerary, legacy.id).revision_number is None


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


def _removable_source(db, trip, *, created_at=None):
    source = Itinerary(
        trip_id=trip.id,
        total_estimated_cost=Decimal("42.00"),
        route_info={"source": "test"},
        weather_info=None,
    )
    if created_at is not None:
        source.created_at = created_at
    db.add(source)
    db.flush()
    day = ItineraryDay(
        itinerary_id=source.id,
        day_number=1,
        date=date(2026, 10, 5),
        title="full",
        summary="Test day",
    )
    db.add(day)
    db.flush()
    target = ItineraryDayItem(
        itinerary_day_id=day.id,
        item_type="attraction",
        title="Remove me",
        start_time=time(9),
        end_time=time(10),
        sort_order=0,
    )
    db.add(target)
    db.flush()
    return source, target


def test_remove_rejects_stale_source_itinerary(db_session):
    trip = _trip(db_session)
    old_source, target = _removable_source(
        db_session, trip, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    _removable_source(
        db_session,
        trip,
        created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    db_session.commit()

    with pytest.raises(ValueError, match="Current itinerary changed"):
        persist_removed_chat_item(db_session, trip.id, old_source.id, target.id)

    assert db_session.query(Itinerary).filter_by(trip_id=trip.id).count() == 2


def test_concurrent_removals_create_only_one_revision(engine):
    with Session(engine) as setup_db:
        trip = _trip(setup_db)
        source, target = _removable_source(setup_db, trip)
        trip_id = trip.id
        source_id = source.id
        target_id = target.id
        setup_db.commit()

    start_together = Barrier(2)
    delay_guard = Lock()
    latest_query_delayed = False

    def delay_first_latest_query(
        _connection, _cursor, statement, _parameters, _context, _executemany
    ):
        nonlocal latest_query_delayed
        normalized = " ".join(statement.upper().split())
        if "ORDER BY ITINERARIES.CREATED_AT DESC" not in normalized:
            return
        with delay_guard:
            should_delay = not latest_query_delayed
            latest_query_delayed = True
        if should_delay:
            # Let the other worker reach the latest check while the first has
            # already acquired its trip lock.
            sleep(0.2)

    event.listen(engine, "after_cursor_execute", delay_first_latest_query)

    def remove_in_own_transaction():
        with Session(engine) as worker_db:
            start_together.wait(timeout=5)
            try:
                persist_removed_chat_item(worker_db, trip_id, source_id, target_id)
                worker_db.commit()
                return "created"
            except ValueError as error:
                worker_db.rollback()
                assert "Current itinerary changed" in str(error)
                return "stale"

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(lambda _index: remove_in_own_transaction(), range(2))
            )
    finally:
        event.remove(engine, "after_cursor_execute", delay_first_latest_query)

    try:
        assert sorted(results) == ["created", "stale"]
        with Session(engine) as check_db:
            revisions = (
                check_db.query(Itinerary)
                .filter_by(trip_id=trip_id)
                .order_by(Itinerary.revision_number)
                .all()
            )
            assert len(revisions) == 2
            revisions_by_id = {row.id: row for row in revisions}
            assert revisions_by_id[source_id].revision_number is None
            created_revision = next(row for row in revisions if row.id != source_id)
            assert created_revision.revision_number == 1
    finally:
        with Session(engine) as cleanup_db:
            itinerary_ids = [
                row.id
                for row in cleanup_db.query(Itinerary.id).filter_by(trip_id=trip_id)
            ]
            day_ids = [
                row.id
                for row in cleanup_db.query(ItineraryDay.id).filter(
                    ItineraryDay.itinerary_id.in_(itinerary_ids)
                )
            ]
            cleanup_db.query(ItineraryDayItem).filter(
                ItineraryDayItem.itinerary_day_id.in_(day_ids)
            ).delete(synchronize_session=False)
            cleanup_db.query(ItineraryDay).filter(ItineraryDay.id.in_(day_ids)).delete(
                synchronize_session=False
            )
            cleanup_db.query(Itinerary).filter_by(trip_id=trip_id).delete(
                synchronize_session=False
            )
            cleanup_db.query(Trip).filter_by(id=trip_id).delete(
                synchronize_session=False
            )
            cleanup_db.commit()
