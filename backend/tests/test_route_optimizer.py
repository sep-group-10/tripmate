from app.services.tools import route_optimizer as optimizer

OPEN_HOURS = {
    day: "08:00-20:00"
    for day in (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
}


def attraction(id_, longitude, start="09:00", end="09:30", **extra):
    return {
        "candidate_id": id_,
        "category": "attraction",
        "name": id_,
        "start_time": start,
        "end_time": end,
        "duration_minutes": 30,
        "latitude": 0.0,
        "longitude": longitude,
        "opening_hours": dict(OPEN_HOURS),
        **extra,
    }


def fixed(id_, category, start, end, longitude=0.0):
    return {
        "candidate_id": id_,
        "category": category,
        "name": id_,
        "start_time": start,
        "end_time": end,
        "latitude": 0.0,
        "longitude": longitude,
    }


def schedule(items, *, day_type="full", hotel_location=None):
    return {
        "status": "ok",
        "days": [
            {
                "day_number": 1,
                "date": "2026-10-05",  # Monday
                "day_type": day_type,
                "items": items,
                "hotel_id": "hotel-1" if hotel_location else None,
                "hotel_location": hotel_location,
                "warnings": ["existing warning"],
            }
        ],
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }


def route_distance(origin_lat, origin_lng, dest_lat, dest_lng):
    from app.services.routing import TravelEstimate

    distance = abs(origin_lng - dest_lng) * 100
    return TravelEstimate(
        duration_minutes=0, distance_km=distance, travel_source="estimate"
    )


def test_known_improvement_reorders_stops_and_recalculates_times(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    original = schedule(
        [attraction("C", 0.03), attraction("A", 0.01), attraction("B", 0.02)],
        hotel_location={"latitude": 0, "longitude": 0},
    )

    result = optimizer.optimize_routes(original)

    items = result["days"][0]["items"]
    assert [item["candidate_id"] for item in items] == ["A", "B", "C"]
    assert [item["start_time"] for item in items] == ["09:00", "09:30", "10:00"]
    assert result["days"][0]["route_optimization"] == {
        "reordered": True,
        "warning": None,
        "local_distance_km": 3.0,
    }
    assert original["days"][0]["items"][0]["candidate_id"] == "C"


def test_fixed_meal_and_event_split_blocks_and_never_move(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    before = [attraction("before-2", 0.03), attraction("before-1", 0.01)]
    lunch = fixed("lunch", "restaurant", "12:30", "13:30", 0.5)
    after = [
        attraction("after-2", 0.08, "14:00", "14:30"),
        attraction("after-1", 0.06, "14:30", "15:00"),
    ]
    event = fixed("event", "local_event", "17:00", "18:00", 0.9)

    result = optimizer.optimize_routes(
        schedule(
            before + [lunch] + after + [event],
            hotel_location={"latitude": 0, "longitude": 0},
        )
    )

    items = result["days"][0]["items"]
    assert [item["candidate_id"] for item in items] == [
        "before-1",
        "before-2",
        "lunch",
        "after-2",
        "after-1",
        "event",
    ]
    assert items[2] == lunch
    assert items[-1] == event
    assert items[0]["end_time"] <= lunch["start_time"]
    assert items[3]["start_time"] >= lunch["end_time"]


def test_block_with_zero_or_one_attraction_is_unchanged():
    for items in ([], [attraction("only", 0.01)]):
        original = schedule(items)
        result = optimizer.optimize_routes(original)
        assert result["days"][0]["items"] == items
        assert result["days"][0]["route_optimization"]["reordered"] is False


def test_missing_coordinates_skips_block_and_names_place(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    first = attraction("first", 0.01)
    second = attraction("No coords", 0.02, latitude=None)
    result = optimizer.optimize_routes(schedule([first, second]))

    assert result["days"][0]["items"] == [first, second]
    assert "No coords" in result["days"][0]["route_optimization"]["warning"]


def test_single_attraction_missing_coordinates_names_place_in_warning():
    no_coords = attraction("No coords", 0.02, latitude=None)
    result = optimizer.optimize_routes(
        schedule([no_coords], hotel_location={"latitude": 0, "longitude": 0})
    )

    assert result["days"][0]["items"] == [no_coords]
    assert result["days"][0]["route_optimization"]["local_distance_km"] == 0.0
    assert "No coords" in result["days"][0]["route_optimization"]["warning"]


def test_routing_failure_keeps_original_block(monkeypatch):
    def fail(*_args):
        raise TimeoutError("routing timed out")

    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", fail)
    original_items = [attraction("a", 0.01), attraction("b", 0.02)]
    result = optimizer.optimize_routes(schedule(original_items))

    assert result["days"][0]["items"] == original_items
    assert (
        result["days"][0]["route_optimization"]["warning"]
        == "Routing failed; original attraction order kept"
    )


def test_time_infeasible_orders_are_rejected(monkeypatch):
    def too_slow(origin, dest):
        from app.services.routing import TravelEstimate

        return TravelEstimate(
            duration_minutes=60,
            distance_km=abs(origin[1] - dest[1]),
            travel_source="estimate",
        )

    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", too_slow)
    items = [
        attraction("a", 0.01, "09:00", "09:30"),
        attraction("b", 0.02, "09:30", "10:00"),
        fixed("event", "local_event", "10:30", "11:00"),
    ]
    result = optimizer.optimize_routes(schedule(items))

    assert result["days"][0]["items"] == items


def test_tied_distances_keep_original_order(monkeypatch):
    from app.services.routing import TravelEstimate

    monkeypatch.setattr(
        optimizer.routing,
        "estimate_travel_time",
        lambda *_: TravelEstimate(
            duration_minutes=0, distance_km=1.0, travel_source="estimate"
        ),
    )
    items = [attraction("b", 0.02), attraction("a", 0.01)]
    assert optimizer.optimize_routes(schedule(items))["days"][0]["items"] == items


def test_day_trip_without_hotel_optimizes_from_first_stop(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    items = [attraction("c", 0.03), attraction("a", 0.01), attraction("b", 0.02)]

    result = optimizer.optimize_routes(schedule(items, day_type="day_trip"))

    assert [item["candidate_id"] for item in result["days"][0]["items"]] != [
        "c",
        "a",
        "b",
    ]


def test_day_with_only_fixed_items_passes_through():
    items = [fixed("lunch", "restaurant", "12:30", "13:30")]
    result = optimizer.optimize_routes(schedule(items))
    assert result["days"][0]["items"] == items
    assert result["days"][0]["route_optimization"]["reordered"] is False


def test_repeated_calls_are_deterministic(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    original = schedule(
        [attraction("c", 0.03), attraction("a", 0.01), attraction("b", 0.02)]
    )

    assert optimizer.optimize_routes(original) == optimizer.optimize_routes(original)


def test_no_feasible_permutation_keeps_original_and_reports_no_reorder(monkeypatch):
    def too_slow(origin, dest):
        from app.services.routing import TravelEstimate

        return TravelEstimate(
            duration_minutes=200,
            distance_km=abs(origin[1] - dest[1]),
            travel_source="estimate",
        )

    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", too_slow)
    items = [attraction("a", 0.01), attraction("b", 0.02)]
    result = optimizer.optimize_routes(schedule(items))
    assert result["days"][0]["items"] == items
    assert result["days"][0]["route_optimization"]["reordered"] is False


def test_large_block_skips_exhaustive_search_with_explanation():
    items = [attraction(f"stop-{index}", index / 100) for index in range(5)]
    result = optimizer.optimize_routes(schedule(items))
    day = result["days"][0]

    assert day["items"] == items
    assert day["route_optimization"]["reordered"] is False
    assert "More than four attractions" in day["route_optimization"]["warning"]


def test_local_distance_includes_final_leg_to_next_anchor(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    items = [
        attraction("A", 0.01, "09:00", "09:30"),
        attraction("B", 0.02, "09:30", "10:00"),
        fixed("lunch", "restaurant", "12:00", "13:00", longitude=0.05),
    ]

    result = optimizer.optimize_routes(
        schedule(items, hotel_location={"latitude": 0, "longitude": 0})
    )

    # hotel(0.00) -> A(0.01) -> B(0.02) -> lunch(0.05): 1 + 1 + 3 = 5 km.
    assert result["days"][0]["route_optimization"]["local_distance_km"] == 5.0


def test_single_attraction_block_counts_hotel_to_attraction_distance(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    items = [attraction("only", 0.03)]

    result = optimizer.optimize_routes(
        schedule(items, hotel_location={"latitude": 0, "longitude": 0})
    )

    # hotel(0.00) -> only(0.03): 3 km.
    assert result["days"][0]["route_optimization"]["local_distance_km"] == 3.0
    assert result["days"][0]["items"] == items


def test_single_attraction_block_routing_failure_keeps_original_and_zero_distance(
    monkeypatch,
):
    def fail(*_args):
        raise TimeoutError("routing timed out")

    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", fail)
    items = [attraction("only", 0.03)]

    result = optimizer.optimize_routes(
        schedule(items, hotel_location={"latitude": 0, "longitude": 0})
    )

    assert result["days"][0]["items"] == items
    assert result["days"][0]["route_optimization"]["local_distance_km"] == 0.0
    assert (
        result["days"][0]["route_optimization"]["warning"]
        == "Routing failed; original attraction order kept"
    )


def test_single_attraction_block_counts_distance_to_next_anchor_too(monkeypatch):
    monkeypatch.setattr(optimizer.routing, "estimate_travel_time", route_distance)
    items = [
        attraction("only", 0.03, "09:00", "09:30"),
        fixed("lunch", "restaurant", "12:00", "13:00", longitude=0.05),
    ]

    result = optimizer.optimize_routes(
        schedule(items, hotel_location={"latitude": 0, "longitude": 0})
    )

    # hotel(0.00) -> only(0.03) -> lunch(0.05): 3 + 2 = 5 km.
    assert result["days"][0]["route_optimization"]["local_distance_km"] == 5.0
