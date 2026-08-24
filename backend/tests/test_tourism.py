def test_create_destination(client):
    response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Test Destination",
            "description": "Pytest destination",
            "country": "Sri Lanka",
            "region": "Central",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.5,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Destination"
    assert data["country"] == "Sri Lanka"
    assert data["rating"] == "4.5"


def test_get_destination(client):
    create_response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Test Get Destination",
            "country": "Sri Lanka",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201
    destination_id = create_response.json()["id"]

    response = client.get(f"/api/v1/destinations/{destination_id}")

    assert response.status_code == 200
    assert response.json()["id"] == destination_id
    assert response.json()["name"] == "Test Get Destination"


def test_update_destination(client):
    create_response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Destination Before Update",
            "country": "Sri Lanka",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201
    destination_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/destinations/{destination_id}",
        json={
            "name": "Destination After Update",
            "rating": 4.8,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Destination After Update"
    assert response.json()["rating"] == "4.8"


def test_soft_delete_destination(client):
    create_response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Destination To Delete",
            "country": "Sri Lanka",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201
    destination_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/destinations/{destination_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    get_response = client.get(f"/api/v1/destinations/{destination_id}")

    assert get_response.status_code == 404


def test_invalid_destination_rating(client):
    response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Invalid Destination",
            "country": "Sri Lanka",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 6,
        },
    )

    assert response.status_code == 400


def test_create_attraction(client):
    response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Test Attraction",
            "description": "Pytest attraction",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "photo_urls": [],
            "rating": 4.5,
            "opening_hours": {},
            "entry_fee": 10,
            "duration_hours": 2,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Attraction"
    assert data["rating"] == "4.5"


def test_get_attraction(client):
    create_response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Test Get Attraction",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "entry_fee": 10,
            "duration_hours": 2,
        },
    )

    assert create_response.status_code == 201
    attraction_id = create_response.json()["id"]

    response = client.get(f"/api/v1/attractions/{attraction_id}")

    assert response.status_code == 200
    assert response.json()["id"] == attraction_id
    assert response.json()["name"] == "Test Get Attraction"


def test_update_attraction(client):
    create_response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Attraction Before Update",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "entry_fee": 10,
            "duration_hours": 2,
        },
    )

    assert create_response.status_code == 201
    attraction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/attractions/{attraction_id}",
        json={
            "name": "Attraction After Update",
            "rating": 4.8,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Attraction After Update"
    assert response.json()["rating"] == "4.8"


def test_soft_delete_attraction(client):
    create_response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Attraction To Delete",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "entry_fee": 10,
            "duration_hours": 2,
        },
    )

    assert create_response.status_code == 201
    attraction_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/attractions/{attraction_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    get_response = client.get(f"/api/v1/attractions/{attraction_id}")

    assert get_response.status_code == 404


def test_invalid_attraction_rating(client):
    response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Invalid Attraction",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 6,
            "entry_fee": 10,
            "duration_hours": 2,
        },
    )

    assert response.status_code == 400


def test_create_hotel(client):
    response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Test Hotel",
            "description": "Pytest hotel",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 100,
            "facilities": ["WiFi", "Pool"],
            "rating": 4.5,
            "photo_urls": [],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Hotel"
    assert data["price_per_night"] == "100.00"
    assert data["rating"] == "4.5"


def test_get_hotel(client):
    create_response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Test Get Hotel",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 120,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201
    hotel_id = create_response.json()["id"]

    response = client.get(f"/api/v1/hotels/{hotel_id}")

    assert response.status_code == 200
    assert response.json()["id"] == hotel_id
    assert response.json()["name"] == "Test Get Hotel"


def test_update_hotel(client):
    create_response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Hotel Before Update",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 100,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201
    hotel_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/hotels/{hotel_id}",
        json={
            "name": "Hotel After Update",
            "price_per_night": 150,
            "rating": 4.8,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Hotel After Update"
    assert response.json()["price_per_night"] == "150.00"
    assert response.json()["rating"] == "4.8"


def test_soft_delete_hotel(client):
    create_response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Hotel To Delete",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 100,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201
    hotel_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/hotels/{hotel_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    get_response = client.get(f"/api/v1/hotels/{hotel_id}")

    assert get_response.status_code == 404


def test_invalid_hotel_rating(client):
    response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Invalid Hotel",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 100,
            "rating": 6,
        },
    )

    assert response.status_code == 400


def test_create_restaurant(client):
    response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Pytest Restaurant",
            "description": "Restaurant created during testing",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "photo_urls": [],
            "operating_hours": {},
            "rating": 4.5,
            "cuisine_type": "Sri Lankan",
            "avg_meal_cost": 15,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Pytest Restaurant"
    assert data["cuisine_type"] == "Sri Lankan"
    assert data["rating"] == "4.5"


def test_get_restaurant(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Test Get Restaurant",
            "description": "Restaurant for GET test",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "cuisine_type": "Chinese",
            "avg_meal_cost": 20,
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    response = client.get(f"/api/v1/restaurants/{restaurant_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == restaurant_id
    assert data["name"] == "Test Get Restaurant"


def test_update_restaurant(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Original Restaurant",
            "description": "Original description",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "cuisine_type": "Sri Lankan",
            "avg_meal_cost": 15,
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/restaurants/{restaurant_id}",
        json={
            "name": "Updated Restaurant",
            "description": "Updated restaurant description",
            "rating": 4.8,
            "avg_meal_cost": 18,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Restaurant"
    assert data["description"] == "Updated restaurant description"
    assert data["rating"] == "4.8"
    assert data["avg_meal_cost"] == "18.00"


def test_soft_delete_restaurant(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Restaurant To Delete",
            "description": "Restaurant for delete test",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "cuisine_type": "Indian",
            "avg_meal_cost": 12,
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/restaurants/{restaurant_id}")

    assert delete_response.status_code == 200

    get_response = client.get(f"/api/v1/restaurants/{restaurant_id}")

    assert get_response.status_code == 404


def test_invalid_restaurant_rating(client):
    response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Invalid Restaurant",
            "description": "Testing validation",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "photo_urls": [],
            "operating_hours": {},
            "rating": 6,
            "cuisine_type": "Sri Lankan",
            "avg_meal_cost": 15,
        },
    )

    assert response.status_code == 400


def test_create_local_event(client):
    response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Pytest Local Event",
            "description": "Local event created during testing",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "photo_urls": [],
            "rating": 4.5,
            "opening_hours": {},
            "duration_hours": 3,
            "entry_fee": 10,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "21:00",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Pytest Local Event"
    assert data["rating"] == "4.5"


def test_get_local_event(client):
    create_response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Test Get Local Event",
            "description": "Event for GET test",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "duration_hours": 2,
            "entry_fee": 5,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "20:00",
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.get(f"/api/v1/local-events/{event_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == event_id
    assert data["name"] == "Test Get Local Event"


def test_update_local_event(client):
    create_response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Original Local Event",
            "description": "Original description",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "duration_hours": 2,
            "entry_fee": 5,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "20:00",
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/local-events/{event_id}",
        json={
            "name": "Updated Local Event",
            "description": "Updated event description",
            "rating": 4.8,
            "duration_hours": 3.5,
            "entry_fee": 12,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Local Event"
    assert data["description"] == "Updated event description"
    assert data["rating"] == "4.8"
    assert data["duration_hours"] == "3.50"
    assert data["entry_fee"] == "12.00"


def test_soft_delete_local_event(client):
    create_response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Event To Delete",
            "description": "Event for delete test",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "duration_hours": 2,
            "entry_fee": 5,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "20:00",
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/local-events/{event_id}")

    assert delete_response.status_code == 200

    get_response = client.get(f"/api/v1/local-events/{event_id}")

    assert get_response.status_code == 404


def test_invalid_local_event_rating(client):
    response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Invalid Local Event",
            "description": "Testing validation",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 6,
            "duration_hours": 3,
            "entry_fee": 10,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "21:00",
            },
        },
    )

    assert response.status_code == 400


def test_search_destinations_case_insensitive_partial(client):
    response = client.get("/api/v1/destinations?search=KAN")

    assert response.status_code == 200

    data = response.json()["data"]
    items = data["items"]

    assert items
    assert all("kan" in item["name"].lower() for item in items)


def test_search_attractions_case_insensitive_partial(client):
    response = client.get("/api/v1/attractions?search=tem")

    assert response.status_code == 200

    items = response.json()

    assert items
    assert all("tem" in item["name"].lower() for item in items)


def test_search_hotels_case_insensitive_partial(client):
    response = client.get("/api/v1/hotels?search=hotel")

    assert response.status_code == 200

    items = response.json()

    assert items
    assert all("hotel" in item["name"].lower() for item in items)


def test_search_restaurants_case_insensitive_partial(client):
    response = client.get("/api/v1/restaurants?search=rest")

    assert response.status_code == 200

    items = response.json()

    assert items
    assert all("rest" in item["name"].lower() for item in items)


def test_search_local_events_case_insensitive_partial(client):
    response = client.get("/api/v1/local-events?search=festival")
    assert response.status_code == 200

    items = response.json()

    assert items
    assert all("festival" in item["name"].lower() for item in items)


def test_filter_destinations_by_region(client):
    response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert response.status_code == 200

    data = response.json()

    for destination in data["data"]["items"]:
        assert "Central" in destination["region"]


def test_filter_attractions_by_region(client):
    response = client.get(
        "/api/v1/attractions",
        params={"region": "Central"},
    )

    assert response.status_code == 200

    items = response.json()

    assert len(items) > 0

    destination_ids = {item["destination_id"] for item in items}

    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]

    central_destination_ids = {destination["id"] for destination in destinations}

    assert destination_ids.issubset(central_destination_ids)


def test_filter_attractions_by_destination(client):
    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    assert len(destinations) > 0

    destination_id = destinations[0]["id"]

    response = client.get(
        "/api/v1/attractions",
        params={"destination_id": destination_id},
    )

    assert response.status_code == 200

    items = response.json()

    for attraction in items:
        assert attraction["destination_id"] == destination_id


def test_filter_hotels_by_region(client):
    response = client.get(
        "/api/v1/hotels",
        params={"region": "Central"},
    )

    assert response.status_code == 200

    items = response.json()
    assert len(items) > 0

    destination_ids = {item["destination_id"] for item in items}

    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    central_destination_ids = {destination["id"] for destination in destinations}

    assert destination_ids.issubset(central_destination_ids)


def test_filter_hotels_by_destination(client):
    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    assert len(destinations) > 0

    destination_id = destinations[0]["id"]

    response = client.get(
        "/api/v1/hotels",
        params={"destination_id": destination_id},
    )

    assert response.status_code == 200

    items = response.json()

    for hotel in items:
        assert hotel["destination_id"] == destination_id


def test_filter_restaurants_by_region(client):
    response = client.get(
        "/api/v1/restaurants",
        params={"region": "Central"},
    )

    assert response.status_code == 200

    items = response.json()
    assert len(items) > 0

    destination_ids = {item["destination_id"] for item in items}

    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    central_destination_ids = {destination["id"] for destination in destinations}

    assert destination_ids.issubset(central_destination_ids)


def test_filter_restaurants_by_destination(client):
    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    assert len(destinations) > 0

    destination_id = destinations[0]["id"]

    response = client.get(
        "/api/v1/restaurants",
        params={"destination_id": destination_id},
    )

    assert response.status_code == 200

    items = response.json()

    for restaurant in items:
        assert restaurant["destination_id"] == destination_id


def test_filter_local_events_by_region(client):
    response = client.get(
        "/api/v1/local-events",
        params={"region": "Central"},
    )

    assert response.status_code == 200

    items = response.json()
    assert len(items) > 0

    destination_ids = {item["destination_id"] for item in items}

    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    central_destination_ids = {destination["id"] for destination in destinations}

    assert destination_ids.issubset(central_destination_ids)


def test_filter_local_events_by_destination(client):
    destination_response = client.get(
        "/api/v1/destinations",
        params={"region": "Central"},
    )

    assert destination_response.status_code == 200

    destinations = destination_response.json()["data"]["items"]
    assert len(destinations) > 0

    destination_id = destinations[0]["id"]

    response = client.get(
        "/api/v1/local-events",
        params={"destination_id": destination_id},
    )

    assert response.status_code == 200

    items = response.json()

    for event in items:
        assert event["destination_id"] == destination_id


def test_soft_deleted_destination_excluded_from_list(client):
    create_response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Deleted Test Destination",
            "description": "Testing soft delete",
            "country": "Sri Lanka",
            "region": "Central",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201

    destination_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/destinations/{destination_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    list_response = client.get(
        "/api/v1/destinations",
    )

    assert list_response.status_code == 200

    items = list_response.json()["data"]["items"]

    returned_ids = {destination["id"] for destination in items}

    assert destination_id not in returned_ids


def test_soft_deleted_destination_excluded_from_search(client):
    create_response = client.post(
        "/api/v1/destinations",
        json={
            "name": "Deleted Search Destination",
            "description": "Testing soft delete search",
            "country": "Sri Lanka",
            "region": "Central",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201

    destination_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/destinations/{destination_id}")

    assert delete_response.status_code == 200

    response = client.get(
        "/api/v1/destinations",
        params={"search": "Deleted Search Destination"},
    )

    assert response.status_code == 200

    items = response.json()["data"]["items"]

    assert all(item["id"] != destination_id for item in items)


def test_soft_deleted_attraction_excluded_from_list(client):
    create_response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Test Attraction",
            "description": "Testing soft delete",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "entry_fee": 10,
        },
    )

    assert create_response.status_code == 201

    attraction_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/attractions/{attraction_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    response = client.get("/api/v1/attractions")

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != attraction_id for item in items)


def test_soft_deleted_attraction_excluded_from_search(client):
    create_response = client.post(
        "/api/v1/attractions",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Search Attraction",
            "description": "Testing soft delete search",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "entry_fee": 10,
        },
    )

    assert create_response.status_code == 201

    attraction_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/attractions/{attraction_id}")

    assert delete_response.status_code == 200

    response = client.get(
        "/api/v1/attractions",
        params={"search": "Deleted Search Attraction"},
    )

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != attraction_id for item in items)


def test_soft_deleted_hotel_excluded_from_list(client):
    create_response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Test Hotel",
            "description": "Testing soft delete",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 100,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201

    hotel_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/hotels/{hotel_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    response = client.get("/api/v1/hotels")

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != hotel_id for item in items)


def test_soft_deleted_hotel_excluded_from_search(client):
    create_response = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Search Hotel",
            "description": "Testing soft delete search",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "price_per_night": 100,
            "rating": 4.0,
        },
    )

    assert create_response.status_code == 201

    hotel_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/hotels/{hotel_id}")

    assert delete_response.status_code == 200

    response = client.get(
        "/api/v1/hotels",
        params={"search": "Deleted Search Hotel"},
    )

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != hotel_id for item in items)


def test_soft_deleted_restaurant_excluded_from_list(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Test Restaurant",
            "description": "Testing soft delete",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "cuisine_type": "Sri Lankan",
            "avg_meal_cost": 15,
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/restaurants/{restaurant_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    response = client.get("/api/v1/restaurants")

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != restaurant_id for item in items)


def test_soft_deleted_restaurant_excluded_from_search(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Search Restaurant",
            "description": "Testing soft delete search",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "cuisine_type": "Sri Lankan",
            "avg_meal_cost": 15,
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/restaurants/{restaurant_id}")

    assert delete_response.status_code == 200

    response = client.get(
        "/api/v1/restaurants",
        params={"search": "Deleted Search Restaurant"},
    )

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != restaurant_id for item in items)


def test_soft_deleted_local_event_excluded_from_list(client):
    create_response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Test Local Event",
            "description": "Testing soft delete",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "duration_hours": 3,
            "entry_fee": 10,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "21:00",
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/local-events/{event_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    response = client.get("/api/v1/local-events")

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != event_id for item in items)


def test_soft_deleted_local_event_excluded_from_search(client):
    create_response = client.post(
        "/api/v1/local-events",
        json={
            "destination_id": "83f7d353-8731-4663-8e79-1a54d473f6dd",
            "name": "Deleted Search Local Event",
            "description": "Testing soft delete search",
            "latitude": 7.2906,
            "longitude": 80.6337,
            "rating": 4.0,
            "duration_hours": 3,
            "entry_fee": 10,
            "event_schedule": {
                "date": "2026-08-25",
                "start_time": "18:00",
                "end_time": "21:00",
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/local-events/{event_id}")

    assert delete_response.status_code == 200

    response = client.get(
        "/api/v1/local-events",
        params={"search": "Deleted Search Local Event"},
    )

    assert response.status_code == 200

    items = response.json()

    assert all(item["id"] != event_id for item in items)
