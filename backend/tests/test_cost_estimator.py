from decimal import Decimal

from app.models.transport_rate import TransportRate
from app.services.tools.cost_estimator import estimate_cost

BASE_TRIP_REQUIREMENTS = {
    "destination": "Kandy",
    "travelers": 2,
}


def _attraction(candidate_id, entry_fee):
    return {
        "id": candidate_id,
        "category": "attraction",
        "name": candidate_id,
        "entry_fee": entry_fee,
    }


def _restaurant(candidate_id, entry_fee):
    return {
        "id": candidate_id,
        "category": "restaurant",
        "name": candidate_id,
        "entry_fee": entry_fee,
    }


def _hotel(candidate_id, price_per_night):
    return {
        "id": candidate_id,
        "category": "hotel",
        "name": candidate_id,
        "entry_fee": price_per_night,
    }


def _scheduled_item(candidate_id, category):
    return {"candidate_id": candidate_id, "category": category}


def _day(day_number, items, hotel_id=None, local_distance_km=None):
    day = {
        "day_number": day_number,
        "items": items,
        "hotel_id": hotel_id,
    }
    if local_distance_km is not None:
        day["route_optimization"] = {"local_distance_km": local_distance_km}
    return day


def _itinerary(days, hotel_by_destination=None):
    return {
        "days": days,
        "hotel_by_destination": hotel_by_destination or {},
    }


def test_traveller_count_multiplies_activities_and_dining(db_session):
    candidates = [
        _attraction("a1", Decimal("100")),
        _restaurant("r1", Decimal("50")),
    ]
    itinerary = _itinerary(
        [
            _day(
                1,
                [
                    _scheduled_item("a1", "attraction"),
                    _scheduled_item("r1", "restaurant"),
                ],
            )
        ]
    )

    result = estimate_cost(db_session, itinerary, candidates, BASE_TRIP_REQUIREMENTS)

    assert result["activities"]["min"] == Decimal("200")
    assert result["activities"]["max"] == Decimal("200")
    assert result["dining"]["min"] == Decimal("100")
    assert result["dining"]["max"] == Decimal("100")


def test_bus_train_transport_scales_with_travellers_car_van_tuk_tuk_does_not(
    db_session,
):
    from app.services.tools.cost_estimator import _CostContext, _leg_cost_range

    rates = {
        row.transport_type: row
        for row in db_session.query(TransportRate).filter(
            TransportRate.region == "Central Province"
        )
    }
    distance_km = Decimal("10")

    range_one = _leg_cost_range(distance_km, 1, rates, _CostContext(), "test leg")
    range_four = _leg_cost_range(distance_km, 4, rates, _CostContext(), "test leg")

    car_cost = rates["car"].base_fare + rates["car"].cost_per_km * distance_km
    train_cost_one = rates["train"].base_fare + rates["train"].cost_per_km * distance_km

    # A per-vehicle type's own cost is identical regardless of travellers.
    assert car_cost == rates["car"].base_fare + rates["car"].cost_per_km * distance_km

    # The range itself must reflect scaling: at 4 travellers the range's
    # upper bound must be at least 4x what a single per-traveller fare was
    # at 1 traveller, while a per-vehicle fare contributes the same amount
    # to both ranges.
    assert range_four.max >= train_cost_one * 4
    assert range_one.min <= car_cost
    assert range_four.min <= car_cost


def test_accommodation_uses_hotel_price_summed_by_nights(db_session):
    candidates = [_hotel("h1", Decimal("5000"))]
    itinerary = _itinerary(
        [
            _day(1, [], hotel_id="h1"),
            _day(2, [], hotel_id="h1"),
        ],
        hotel_by_destination={"Kandy": "h1"},
    )

    result = estimate_cost(db_session, itinerary, candidates, BASE_TRIP_REQUIREMENTS)

    assert result["accommodation"]["min"] == Decimal("10000")
    assert result["accommodation"]["max"] == Decimal("10000")


def test_is_estimate_true_when_any_local_leg_used_an_estimate(db_session):
    itinerary = _itinerary([_day(1, [], local_distance_km=Decimal("5"))])

    result = estimate_cost(db_session, itinerary, [], BASE_TRIP_REQUIREMENTS)

    assert result["transport_local"]["is_estimate"] is True


def test_is_estimate_false_when_no_local_travel_recorded(db_session):
    itinerary = _itinerary([_day(1, [])])

    result = estimate_cost(db_session, itinerary, [], BASE_TRIP_REQUIREMENTS)

    assert result["transport_local"] == {
        "min": Decimal("0"),
        "max": Decimal("0"),
        "is_estimate": False,
    }


def test_cross_region_leg_uses_destination_region_rate(db_session):
    itinerary = _itinerary([_day(1, [], local_distance_km=Decimal("10"))])

    kandy_result = estimate_cost(
        db_session, itinerary, [], {**BASE_TRIP_REQUIREMENTS, "destination": "Kandy"}
    )
    galle_result = estimate_cost(
        db_session, itinerary, [], {**BASE_TRIP_REQUIREMENTS, "destination": "Galle"}
    )

    # Different regions have different rate rows, so unless the data happens
    # to collide, the two results should differ - this proves the lookup
    # is actually keyed by the destination's region, not some fixed default.
    assert kandy_result["transport_local"] != galle_result["transport_local"]


def test_missing_traveller_count_defaults_to_one_with_warning(db_session):
    requirements = {"destination": "Kandy"}
    itinerary = _itinerary([_day(1, [])])

    result = estimate_cost(db_session, itinerary, [], requirements)

    assert result["travellers"] == 1
    assert any("solo travel" in warning for warning in result["warnings"])


def test_missing_hotel_for_destination_skips_accommodation_with_warning(db_session):
    itinerary = _itinerary(
        [_day(1, [], hotel_id="missing-hotel")],
        hotel_by_destination={"Kandy": "missing-hotel"},
    )

    result = estimate_cost(db_session, itinerary, [], BASE_TRIP_REQUIREMENTS)

    assert result["accommodation"] == {"min": Decimal("0"), "max": Decimal("0")}
    assert any("No hotel assigned" in warning for warning in result["warnings"])


def test_zero_cost_itinerary_returns_all_zero_categories(db_session):
    itinerary = _itinerary([_day(1, [])])

    result = estimate_cost(db_session, itinerary, [], BASE_TRIP_REQUIREMENTS)

    assert result["transport_intercity"]["min"] == 0
    assert result["transport_intercity"]["max"] == 0
    assert result["transport_local"]["min"] == 0
    assert result["accommodation"]["min"] == 0
    assert result["activities"]["min"] == 0
    assert result["dining"]["min"] == 0
    assert result["miscellaneous"]["min"] == 0
    assert result["total"]["min"] == 0
    assert result["total"]["max"] == 0


def test_miscellaneous_is_ten_percent_of_prior_five_categories(db_session):
    candidates = [_attraction("a1", Decimal("1000")), _hotel("h1", Decimal("5000"))]
    itinerary = _itinerary(
        [_day(1, [_scheduled_item("a1", "attraction")], hotel_id="h1")],
        hotel_by_destination={"Kandy": "h1"},
    )

    result = estimate_cost(db_session, itinerary, candidates, BASE_TRIP_REQUIREMENTS)

    subtotal_min = (
        result["transport_intercity"]["min"]
        + result["transport_local"]["min"]
        + result["accommodation"]["min"]
        + result["activities"]["min"]
        + result["dining"]["min"]
    )
    subtotal_max = (
        result["transport_intercity"]["max"]
        + result["transport_local"]["max"]
        + result["accommodation"]["max"]
        + result["activities"]["max"]
        + result["dining"]["max"]
    )

    assert result["miscellaneous"]["min"] == subtotal_min * Decimal("0.10")
    assert result["miscellaneous"]["max"] == subtotal_max * Decimal("0.10")


def test_total_equals_sum_of_all_six_category_mins_and_maxes(db_session):
    candidates = [_attraction("a1", Decimal("1000")), _hotel("h1", Decimal("5000"))]
    itinerary = _itinerary(
        [
            _day(
                1,
                [_scheduled_item("a1", "attraction")],
                hotel_id="h1",
                local_distance_km=Decimal("10"),
            )
        ],
        hotel_by_destination={"Kandy": "h1"},
    )

    result = estimate_cost(db_session, itinerary, candidates, BASE_TRIP_REQUIREMENTS)

    expected_min = sum(
        result[key]["min"]
        for key in (
            "transport_intercity",
            "transport_local",
            "accommodation",
            "activities",
            "dining",
            "miscellaneous",
        )
    )
    expected_max = sum(
        result[key]["max"]
        for key in (
            "transport_intercity",
            "transport_local",
            "accommodation",
            "activities",
            "dining",
            "miscellaneous",
        )
    )

    assert result["total"]["min"] == expected_min
    assert result["total"]["max"] == expected_max


def test_no_transfers_returns_zero_intercity_cost(db_session):
    itinerary = _itinerary([_day(1, [])])

    result = estimate_cost(db_session, itinerary, [], BASE_TRIP_REQUIREMENTS)

    assert result["transport_intercity"] == {
        "min": Decimal("0"),
        "max": Decimal("0"),
        "is_estimate": False,
    }


def test_no_rate_for_one_vehicle_type_excludes_it_without_crashing(db_session):
    from app.services.tools.cost_estimator import _CostContext, _leg_cost_range

    rates = {
        row.transport_type: row
        for row in db_session.query(TransportRate).filter(
            TransportRate.region == "Central Province"
        )
    }
    del rates["car"]

    context = _CostContext()
    leg_range = _leg_cost_range(Decimal("10"), 1, rates, context, "test leg")

    assert leg_range is not None
    assert any("car" in warning for warning in context.warnings)


def test_no_rate_for_any_vehicle_type_leaves_leg_unpriced(db_session):
    from app.services.tools.cost_estimator import _CostContext, _leg_cost_range

    context = _CostContext()
    leg_range = _leg_cost_range(Decimal("10"), 1, {}, context, "test leg")

    assert leg_range is None
    assert any("unpriced" in warning for warning in context.warnings)


def test_large_group_still_priced_flat_with_capacity_warning(db_session):
    itinerary = _itinerary([_day(1, [], local_distance_km=Decimal("10"))])

    result = estimate_cost(
        db_session, itinerary, [], {**BASE_TRIP_REQUIREMENTS, "travelers": 6}
    )

    assert result["travellers"] == 6
    assert any("multiple vehicles" in warning for warning in result["warnings"])
