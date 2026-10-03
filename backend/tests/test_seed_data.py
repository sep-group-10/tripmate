import re
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.check_seed_data import (
    covers_dinner,
    find_destinations_short_on_dinner,
    find_destinations_without_hotel,
    find_far_places,
    find_past_events,
    find_price_outliers,
)
from app.core.seed_data import DESTINATION_SEEDS, TRANSPORT_RATES
from app.core.seed_data.commons_photos import (
    ATTRACTION_PHOTO_URLS,
    COMMONS_URL_PREFIX,
    GENERIC_PHOTO_URLS,
    KNOWN_WRONG_PHOTO_NAMES,
    event_photo,
    hotel_photo,
    restaurant_photo,
)
from app.core.seed_data.photo_credits import PHOTO_CREDITS
from app.core.seed_data.photos import (
    ATTRACTION_PHOTOS,
    EVENT_PHOTOS,
    HOTEL_PHOTOS,
    PHOTO_CDN,
    RESTAURANT_PHOTOS,
)
from app.core.seed_tourism import seed_tourism
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant
from app.models.transport_rate import TransportRate

SEEDED_NAMES = {data["name"] for data in DESTINATION_SEEDS}
PLANNER_READY = [d for d in DESTINATION_SEEDS if d.get("planner_ready", True)]
PLACE_MODELS = (Attraction, Hotel, Restaurant, LocalEvent)


def _counts(db):
    return {
        model.__tablename__: db.query(model).count()
        for model in (Destination, TransportRate, *PLACE_MODELS)
    }


def _active_places(db, destination_name):
    destination = db.query(Destination).filter_by(name=destination_name).one()
    return destination, [
        (model, row)
        for model in PLACE_MODELS
        for row in db.query(model).filter_by(
            destination_id=destination.id, is_active=True
        )
    ]


def test_seeding_twice_creates_no_duplicates(db_session):
    seed_tourism(db_session)
    after_first = _counts(db_session)

    seed_tourism(db_session)
    seed_tourism(db_session)

    assert _counts(db_session) == after_first

    for data in DESTINATION_SEEDS:
        destination = db_session.query(Destination).filter_by(name=data["name"]).one()
        for model, key in (
            (Attraction, "attractions"),
            (Hotel, "hotels"),
            (Restaurant, "restaurants"),
            (LocalEvent, "events"),
        ):
            for item in data[key]:
                active = (
                    db_session.query(model)
                    .filter_by(
                        destination_id=destination.id,
                        name=item["name"],
                        is_active=True,
                    )
                    .count()
                )
                assert active == 1, f"{data['name']}: {item['name']} x{active}"


def test_reseeding_corrects_existing_rows_and_never_deletes(db_session):
    hotel = db_session.query(Hotel).filter_by(name="Cinnamon Grand Kandy Retreat").one()
    hotel.price_per_night = Decimal("25000.00")
    hotel.is_active = False
    db_session.add(
        TransportRate(
            transport_type="ferry",
            region="Western Province",
            cost_per_km=Decimal("1.00"),
            base_fare=Decimal("1.00"),
        )
    )
    db_session.commit()
    before = _counts(db_session)

    seed_tourism(db_session)

    db_session.refresh(hotel)
    assert hotel.price_per_night == Decimal("220.00")
    assert hotel.is_active is True
    # Rates outside the seed are left alone, and nothing is removed.
    assert (
        db_session.query(TransportRate).filter_by(transport_type="ferry").count() == 1
    )
    assert _counts(db_session) == before


def test_seed_data_has_no_name_collisions_with_deactivation_lists():
    for data in DESTINATION_SEEDS:
        seeded = {a["name"].lower() for a in data["attractions"]}
        assert seeded.isdisjoint(
            n.lower() for n in data.get("deactivate_attractions", [])
        )


@pytest.mark.parametrize("destination", SEEDED_NAMES)
def test_every_active_place_is_within_30_km_of_its_destination(db_session, destination):
    seed_tourism(db_session)

    far = [p for p in find_far_places(db_session) if p["destination"] == destination]

    assert far == []


@pytest.mark.parametrize("data", PLANNER_READY, ids=lambda d: d["name"])
def test_active_destination_has_a_hotel_and_enough_short_attractions(db_session, data):
    seed_tourism(db_session)
    destination = db_session.query(Destination).filter_by(name=data["name"]).one()
    assert destination.is_active

    hotels = db_session.query(Hotel).filter_by(
        destination_id=destination.id, is_active=True
    )
    short_attractions = db_session.query(Attraction).filter(
        Attraction.destination_id == destination.id,
        Attraction.is_active.is_(True),
        Attraction.duration_hours <= 3,
    )

    assert hotels.count() >= 1
    assert short_attractions.count() >= 8
    assert data["name"] not in find_destinations_without_hotel(db_session)


@pytest.mark.parametrize("data", PLANNER_READY, ids=lambda d: d["name"])
def test_destination_has_three_dinner_restaurants(db_session, data):
    seed_tourism(db_session)

    short = find_destinations_short_on_dinner(db_session)

    assert data["name"] not in {item["destination"] for item in short}


@pytest.mark.parametrize("data", PLANNER_READY, ids=lambda d: d["name"])
def test_place_coordinates_are_real_and_distinct(db_session, data):
    seed_tourism(db_session)
    destination, places = _active_places(db_session, data["name"])

    coordinates = [(row.latitude, row.longitude) for _, row in places]

    assert (destination.latitude, destination.longitude) not in coordinates
    assert len(set(coordinates)) == len(coordinates)


@pytest.mark.parametrize("data", PLANNER_READY, ids=lambda d: d["name"])
def test_every_row_has_a_description(db_session, data):
    seed_tourism(db_session)
    _, places = _active_places(db_session, data["name"])

    assert places
    assert all(row.description and row.description.strip() for _, row in places)


def test_events_are_dated_relative_to_the_seed_run_date(db_session):
    today = date(2031, 3, 1)

    seed_tourism(db_session, today=today)

    for data in DESTINATION_SEEDS:
        assert len(data["events"]) in (0, 2)
        destination = db_session.query(Destination).filter_by(name=data["name"]).one()
        for item in data["events"]:
            event = (
                db_session.query(LocalEvent)
                .filter_by(destination_id=destination.id, name=item["name"])
                .one()
            )
            assert (
                today + timedelta(days=30)
                <= event.starts_on
                <= today + timedelta(days=240)
            )
            assert event.ends_on >= event.starts_on
            assert event.event_schedule["start_time"] == item["start_time"]
            assert event.event_schedule["end_time"] == item["end_time"]
            assert event.rating is not None
    assert not [
        e
        for e in find_past_events(db_session, today)
        if e["destination"] in SEEDED_NAMES
    ]


def test_nine_arch_bridge_is_active_only_under_ella(db_session):
    seed_tourism(db_session)

    def active_bridges(destination_name):
        destination = (
            db_session.query(Destination).filter_by(name=destination_name).one()
        )
        return (
            db_session.query(Attraction)
            .filter(
                Attraction.destination_id == destination.id,
                Attraction.is_active.is_(True),
                Attraction.name.ilike("nine arch%"),
            )
            .all()
        )

    assert [b.name for b in active_bridges("Ella")] == ["Nine Arch Bridge"]
    assert active_bridges("Kandy") == []
    assert active_bridges("Galle") == []
    assert (
        db_session.query(Destination).filter_by(name="Ella").one().region
        == "Uva Province"
    )


def test_every_seeded_region_has_all_transport_types(db_session):
    seed_tourism(db_session)

    needed = {"bus_budget", "bus_luxury", "train", "tuk_tuk", "car", "van"}
    for region in {data["region"] for data in DESTINATION_SEEDS}:
        have = {
            rate.transport_type
            for rate in db_session.query(TransportRate).filter_by(region=region)
        }
        assert needed <= have, region
    assert len(TRANSPORT_RATES) == len(
        {(r["transport_type"], r["region"]) for r in TRANSPORT_RATES}
    )


def test_seeded_prices_are_in_the_normal_range(db_session):
    seed_tourism(db_session)

    outliers = [
        o for o in find_price_outliers(db_session) if o["destination"] in SEEDED_NAMES
    ]

    assert outliers == []


def test_covers_dinner_requires_the_whole_slot_every_day():
    assert covers_dinner({d: "11:00-22:00" for d in _days()})
    assert not covers_dinner({d: "08:00-17:00" for d in _days()})
    assert not covers_dinner({d: "11:00-19:30" for d in _days()})
    assert not covers_dinner(
        {**{d: "11:00-22:00" for d in _days()}, "sunday": "closed"}
    )
    assert not covers_dinner(None)


def _days():
    return (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )


# --- photos -----------------------------------------------------------------

_ALLOWED_LICENSE = re.compile(r"^(CC0|CC BY(-SA)? \d|Public domain)", re.IGNORECASE)
_GENERIC_KEYS = {
    "budget_room",
    "midrange_room",
    "resort_pool",
    "rice_and_curry",
    "seafood",
    "cafe",
    "street_food",
    "indian_curry",
    "noodles",
    "festival",
    "perahera",
    "beach_event",
}


def test_photo_credits_are_complete_and_use_allowed_licenses():
    assert {c["name"] for c in PHOTO_CREDITS if c["kind"] == "generic"} == _GENERIC_KEYS
    for credit in PHOTO_CREDITS:
        label = credit["used_for"]
        assert credit["url"].startswith("https://upload.wikimedia.org/"), label
        assert "/960px-" in credit["url"], label
        assert _ALLOWED_LICENSE.match(credit["license"]), label
        assert credit["author"].strip() and len(credit["author"]) < 120, label
        assert credit["source"].startswith("https://commons.wikimedia.org/wiki/File:")
    urls = [credit["url"] for credit in PHOTO_CREDITS]
    assert len(urls) == len(set(urls))


def test_every_credited_attraction_exists_in_the_seed_data():
    seeded = {a["name"] for d in DESTINATION_SEEDS for a in d["attractions"]}
    assert set(ATTRACTION_PHOTO_URLS) <= seeded


@pytest.mark.parametrize("data", DESTINATION_SEEDS, ids=lambda d: d["name"])
def test_each_destination_has_at_least_three_attractions_with_photos(data):
    with_photo = [
        a["name"]
        for a in data["attractions"]
        if a["name"] in ATTRACTION_PHOTOS or a["name"] in ATTRACTION_PHOTO_URLS
    ]
    assert len(with_photo) >= 3


def test_every_hotel_restaurant_and_event_gets_a_photo(db_session):
    seed_tourism(db_session)

    for model in (Hotel, Restaurant, LocalEvent):
        for data in DESTINATION_SEEDS:
            destination = (
                db_session.query(Destination).filter_by(name=data["name"]).one()
            )
            rows = db_session.query(model).filter_by(
                destination_id=destination.id, is_active=True
            )
            for row in rows:
                assert row.photo_urls, f"{data['name']}: {row.name}"
                url = row.photo_urls[0]
                assert url.startswith((COMMONS_URL_PREFIX, PHOTO_CDN)), row.name


def test_existing_photo_map_entries_are_kept(db_session):
    seed_tourism(db_session)

    for model, photos in (
        (Attraction, ATTRACTION_PHOTOS),
        (Hotel, HOTEL_PHOTOS),
        (Restaurant, RESTAURANT_PHOTOS),
        (LocalEvent, EVENT_PHOTOS),
    ):
        for name, key in photos.items():
            rows = db_session.query(model).filter_by(name=name, is_active=True).all()
            for row in rows:
                assert row.photo_urls == [f"{PHOTO_CDN}/{key}"], name


def test_reseeding_keeps_other_existing_photos_but_replaces_known_wrong_ones(
    db_session,
):
    custom = ["https://example.com/admin-upload.jpg"]
    museum = db_session.query(Attraction).filter_by(name="Sigiriya Museum").one()
    lodge = db_session.query(Hotel).filter_by(name="Ella Budget Lodge").one()
    galle_fort = db_session.query(Attraction).filter_by(name="Galle Fort").one()
    assert "Galle Fort" in KNOWN_WRONG_PHOTO_NAMES
    museum.photo_urls = custom
    lodge.photo_urls = custom
    galle_fort.photo_urls = ["https://example.com/wrong-photo.jpg"]
    db_session.commit()

    seed_tourism(db_session)
    db_session.refresh(museum)
    db_session.refresh(lodge)
    db_session.refresh(galle_fort)

    assert museum.photo_urls == custom
    assert lodge.photo_urls == custom
    assert galle_fort.photo_urls == [ATTRACTION_PHOTO_URLS["Galle Fort"]]


def test_generic_photos_are_matched_by_type_and_price():
    assert hotel_photo({"price_per_night": 38}) == GENERIC_PHOTO_URLS["budget_room"]
    assert hotel_photo({"price_per_night": 95}) == GENERIC_PHOTO_URLS["midrange_room"]
    assert hotel_photo({"price_per_night": 220}) == GENERIC_PHOTO_URLS["resort_pool"]

    for cuisine, key in (
        ("Local Sri Lankan", "rice_and_curry"),
        ("Seafood", "seafood"),
        ("Western", "cafe"),
        ("Indian", "indian_curry"),
        ("Chinese", "noodles"),
        ("Thai", "street_food"),
    ):
        assert restaurant_photo({"cuisine_type": cuisine}) == GENERIC_PHOTO_URLS[key]

    for name, key in (
        ("Kandy Esala Perahera", "perahera"),
        ("Negombo Lagoon Lantern Night", "perahera"),
        ("Colombo Food and Culture Fair", "street_food"),
        ("Mirissa Whale and Ocean Festival", "beach_event"),
        ("Kandy Traditional Arts Exhibition", "festival"),
    ):
        assert event_photo({"name": name}) == GENERIC_PHOTO_URLS[key]
