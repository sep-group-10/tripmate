from decimal import Decimal

from app.core.database import SessionLocal
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant

HOTELS = {
    "Kandy": [
        {
            "name": "Kandy Heritage Hotel",
            "description": (
                "Comfortable budget accommodation near central Kandy and Kandy Lake."
            ),
            "price_per_night": Decimal("42.00"),
            "facilities": ["WiFi", "Breakfast", "Air Conditioning", "Parking"],
            "rating": Decimal("4.1"),
        },
        {
            "name": "Hill View Kandy",
            "description": (
                "Affordable hotel with scenic views of the surrounding hills."
            ),
            "price_per_night": Decimal("65.00"),
            "facilities": ["WiFi", "Restaurant", "Room Service", "Parking"],
            "rating": Decimal("4.2"),
        },
        {
            "name": "Kandy Lake Residence",
            "description": (
                "Mid-range accommodation within easy reach of Kandy Lake "
                "and cultural attractions."
            ),
            "price_per_night": Decimal("95.00"),
            "facilities": ["WiFi", "Restaurant", "Swimming Pool", "Breakfast"],
            "rating": Decimal("4.4"),
        },
        {
            "name": "Royal Hills Kandy",
            "description": (
                "Upscale hotel offering comfortable rooms and panoramic "
                "mountain views."
            ),
            "price_per_night": Decimal("165.00"),
            "facilities": ["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
            "rating": Decimal("4.6"),
        },
        {
            "name": "Cinnamon Grand Kandy Retreat",
            "description": (
                "Luxury-style accommodation with premium facilities and "
                "elegant rooms."
            ),
            "price_per_night": Decimal("220.00"),
            "facilities": [
            "WiFi",
            "Spa",
            "Pool",
            "Fine Dining",
            "Gym",
            "Airport Transfer",
        ],
            "rating": Decimal("4.8"),
        },
    ],
    "Colombo": [
        {
            "name": "Colombo City Budget Hotel",
            "description": (
                "Affordable accommodation close to shopping and city attractions."
            ),
            "price_per_night": Decimal("35.00"),
            "facilities": ["WiFi", "Breakfast", "Air Conditioning"],
            "rating": Decimal("4.0"),
        },
        {
            "name": "Ocean View Colombo",
            "description": (
                "Comfortable mid-range hotel overlooking the Colombo coastline."
            ),
            "price_per_night": Decimal("78.00"),
            "facilities": ["WiFi", "Restaurant", "Sea View", "Breakfast"],
            "rating": Decimal("4.2"),
        },
        {
            "name": "Colombo Central Hotel",
            "description": (
                "Modern hotel convenient for business travellers and tourists."
            ),
            "price_per_night": Decimal("110.00"),
            "facilities": ["WiFi", "Restaurant", "Gym", "Room Service"],
            "rating": Decimal("4.4"),
        },
        {
            "name": "Marina Colombo",
            "description": "Upscale coastal hotel with modern rooms and city views.",
            "price_per_night": Decimal("175.00"),
            "facilities": ["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
            "rating": Decimal("4.6"),
        },
        {
            "name": "Colombo Grand Palace",
            "description": (
                "Luxury city hotel with premium dining and wellness facilities."
            ),
            "price_per_night": Decimal("260.00"),
            "facilities": [
    "WiFi",
    "Spa",
    "Pool",
    "Fine Dining",
    "Gym",
    "Concierge",
],
"rating": Decimal("4.8"),
},
    ],
    "Galle": [
        {
            "name": "Galle Fort Budget Stay",
            "description": (
                "Affordable accommodation close to the historic Galle Fort."
            ),
            "price_per_night": Decimal("38.00"),
            "facilities": ["WiFi", "Breakfast", "Air Conditioning"],
            "rating": Decimal("4.0"),
        },
        {
            "name": "Southern Coast Hotel",
            "description": (
                "Comfortable hotel near Galle's beaches and historic attractions."
            ),
            "price_per_night": Decimal("72.00"),
            "facilities": ["WiFi", "Restaurant", "Parking", "Breakfast"],
            "rating": Decimal("4.2"),
        },
        {
            "name": "Galle Heritage Residence",
            "description": (
                "Stylish accommodation inspired by the historic architecture of Galle."
            ),
            "price_per_night": Decimal("125.00"),
            "facilities": ["WiFi", "Restaurant", "Garden", "Breakfast"],
            "rating": Decimal("4.5"),
        },
        {
            "name": "Ocean Breeze Galle",
            "description": "Upscale coastal hotel with relaxing ocean views.",
            "price_per_night": Decimal("180.00"),
            "facilities": ["WiFi", "Pool", "Restaurant", "Spa", "Sea View"],
            "rating": Decimal("4.6"),
        },
        {
            "name": "Galle Fort Luxury Retreat",
            "description": (
                "Premium accommodation combining colonial character "
                "with modern luxury."
            ),
            "price_per_night": Decimal("240.00"),
            "facilities": [
    "WiFi",
    "Pool",
    "Spa",
    "Fine Dining",
    "Gym",
    "Concierge",
],
"rating": Decimal("4.9"),
},
    ],
}


ATTRACTIONS = {
    "Kandy": [
        (
            "Temple of the Sacred Tooth Relic",
            "Religious",
            (
                "Historic Buddhist temple and one of Sri Lanka's most important "
                "religious sites."
            ),
            2.0,
            4.9,
            7.2936,
            80.6413,
        ),
        (
            "Kandy Lake",
            "Nature",
            "Scenic artificial lake located in the heart of Kandy.",
            1.5,
            4.6,
            7.2936,
            80.6413,
        ),
        (
            "Royal Botanical Gardens",
            "Nature",
            "Large botanical garden famous for tropical plants and orchids.",
            3.0,
            4.7,
            7.2697,
            80.5966,
        ),
        (
            "Bahirawakanda Temple",
            "Religious",
            "Hilltop Buddhist temple offering panoramic views of Kandy.",
            1.5,
            4.5,
            7.2909,
            80.6266,
        ),
        (
            "Kandy National Museum",
            "Historical",
            "Museum displaying artefacts related to Kandy's royal history.",
            2.0,
            4.3,
            7.2944,
            80.6412,
        ),
        (
            "Udawattakele Forest Reserve",
            "Nature",
            "Forest reserve offering walking trails and rich biodiversity.",
            3.0,
            4.6,
            7.3006,
            80.6465,
        ),
        (
            "Kandy Cultural Dance Centre",
            "Cultural",
            "Venue showcasing traditional Sri Lankan dance performances.",
            1.5,
            4.5,
            7.2925,
            80.6418,
        ),
        (
            "World Buddhist Museum",
            "Cultural",
            "Museum presenting Buddhist heritage from different countries.",
            2.0,
            4.4,
            7.2939,
            80.6412,
        ),
        (
            "Knuckles Mountain Range",
            "Adventure",
            "Mountain area offering hiking and nature experiences.",
            6.0,
            4.8,
            7.4500,
            80.8000,
        ),
        (
            "Ambuluwawa Tower",
            "Adventure",
            "Unique tower surrounded by mountain scenery and hiking trails.",
            3.0,
            4.7,
            7.1269,
            80.6385,
        ),
    ],
    "Colombo": [
        (
            "Gangaramaya Temple",
            "Religious",
            "Historic Buddhist temple featuring religious and cultural collections.",
            2.0,
            4.6,
            6.9167,
            79.8560,
        ),
        (
            "Jami Ul-Alfar Mosque",
            "Religious",
            "Distinctive historic mosque in the Pettah area.",
            1.0,
            4.4,
            6.9369,
            79.8500,
        ),
        (
            "Galle Face Green",
            "Nature",
            "Popular seaside promenade ideal for sunset walks.",
            2.0,
            4.5,
            6.9271,
            79.8436,
        ),
        (
            "Viharamahadevi Park",
            "Nature",
            "Large public park in central Colombo.",
            2.0,
            4.4,
            6.9147,
            79.8612,
        ),
        (
            "Colombo National Museum",
            "Historical",
            "Major museum documenting Sri Lanka's history and heritage.",
            2.5,
            4.6,
            6.9107,
            79.8587,
        ),
        (
            "Colombo Fort",
            "Historical",
            "Historic commercial district containing colonial-era buildings.",
            2.0,
            4.3,
            6.9344,
            79.8428,
        ),
        (
            "Independence Memorial Hall",
            "Cultural",
            "National monument commemorating Sri Lanka's independence.",
            1.5,
            4.5,
            6.9057,
            79.8692,
        ),
        (
            "Colombo Lotus Tower",
            "Cultural",
            "Iconic communications tower with observation facilities.",
            2.0,
            4.6,
            6.9271,
            79.8612,
        ),
        (
            "Bolgoda Lake",
            "Adventure",
            "Large lake offering boating and outdoor activities.",
            3.0,
            4.4,
            6.7780,
            79.9200,
        ),
        (
            "Mount Lavinia Beach",
            "Adventure",
            "Popular beach suitable for swimming and coastal activities.",
            3.0,
            4.5,
            6.8344,
            79.8637,
        ),
    ],
    "Galle": [
        (
            "Galle Fort",
            "Historical",
            "UNESCO-listed historic fortification overlooking the Indian Ocean.",
            3.0,
            4.9,
            6.0329,
            80.2168,
        ),
        (
            "Dutch Reformed Church",
            "Religious",
            "Historic church located inside Galle Fort.",
            1.0,
            4.4,
            6.0285,
            80.2166,
        ),
        (
            "Galle Lighthouse",
            "Historical",
            "Historic lighthouse overlooking the southern coastline.",
            1.5,
            4.7,
            6.0269,
            80.2182,
        ),
        (
            "Jungle Beach",
            "Nature",
            "Secluded beach surrounded by tropical vegetation.",
            3.0,
            4.6,
            6.0140,
            80.2460,
        ),
        (
            "Unawatuna Beach",
            "Nature",
            "Popular sandy beach known for swimming and coastal scenery.",
            3.0,
            4.7,
            6.0090,
            80.2490,
        ),
        (
            "Martin Wickramasinghe Museum",
            "Cultural",
            "Museum dedicated to Sri Lankan writer Martin Wickramasinghe.",
            1.5,
            4.3,
            6.0317,
            80.3378,
        ),
        (
            "National Maritime Museum",
            "Historical",
            "Museum covering the maritime history of Galle.",
            2.0,
            4.4,
            6.0276,
            80.2170,
        ),
        (
            "Japanese Peace Pagoda",
            "Religious",
            "White Buddhist pagoda located on Rumassala Hill.",
            1.5,
            4.7,
            6.0110,
            80.2470,
        ),
        (
            "Rumassala Forest",
            "Adventure",
            "Forest area with walking trails and coastal views.",
            3.0,
            4.5,
            6.0120,
            80.2440,
        ),
        (
            "Koggala Lake",
            "Adventure",
            "Scenic lagoon offering boat rides and wildlife experiences.",
            3.0,
            4.6,
            5.9970,
            80.3200,
        ),
    ],
}


RESTAURANTS = {
    "Kandy": [
        ("Kandy Spice Garden", "Local Sri Lankan", Decimal("12.00"), 4.5),
        ("Kandy Indian Kitchen", "Indian", Decimal("15.00"), 4.3),
        ("Lake View Chinese Restaurant", "Chinese", Decimal("14.00"), 4.2),
        ("Hilltop Western Bistro", "Western", Decimal("22.00"), 4.4),
        ("Kandy Lake Seafood House", "Seafood", Decimal("25.00"), 4.6),
    ],
    "Colombo": [
        ("Colombo Heritage Kitchen", "Local Sri Lankan", Decimal("14.00"), 4.6),
        ("Pettah Indian Restaurant", "Indian", Decimal("16.00"), 4.3),
        ("Colombo Dragon Palace", "Chinese", Decimal("20.00"), 4.4),
        ("Ocean Terrace Bistro", "Western", Decimal("28.00"), 4.5),
        ("Colombo Seafood Harbour", "Seafood", Decimal("32.00"), 4.7),
    ],
    "Galle": [
        ("Galle Spice House", "Local Sri Lankan", Decimal("13.00"), 4.6),
        ("Galle Indian Garden", "Indian", Decimal("16.00"), 4.4),
        ("Fort Chinese Kitchen", "Chinese", Decimal("18.00"), 4.2),
        ("Fort Western Bistro", "Western", Decimal("24.00"), 4.5),
        ("Southern Coast Seafood", "Seafood", Decimal("30.00"), 4.7),
    ],
}


EVENTS = {
    "Kandy": [
        {
            "name": "Kandy Cultural Heritage Festival",
            "event_schedule": {
                "date": "2026-08-20",
                "start_time": "18:00",
                "end_time": "21:00",
            },
            "entry_fee": Decimal("10.00"),
        },
        {
            "name": "Kandy Traditional Arts Exhibition",
            "event_schedule": {
                "date": "2026-09-05",
                "start_time": "10:00",
                "end_time": "17:00",
            },
            "entry_fee": Decimal("5.00"),
        },
    ],
    "Colombo": [
        {
            "name": "Colombo Food and Culture Fair",
            "event_schedule": {
                "date": "2026-08-22",
                "start_time": "11:00",
                "end_time": "20:00",
            },
            "entry_fee": Decimal("8.00"),
        },
        {
            "name": "Colombo Coastal Music Festival",
            "event_schedule": {
                "date": "2026-09-12",
                "start_time": "16:00",
                "end_time": "22:00",
            },
            "entry_fee": Decimal("15.00"),
        },
    ],
    "Galle": [
        {
            "name": "Galle Fort Heritage Festival",
            "event_schedule": {
                "date": "2026-08-29",
                "start_time": "10:00",
                "end_time": "20:00",
            },
            "entry_fee": Decimal("7.00"),
        },
        {
            "name": "Southern Coast Seafood Festival",
            "event_schedule": {
                "date": "2026-09-19",
                "start_time": "12:00",
                "end_time": "21:00",
            },
            "entry_fee": Decimal("10.00"),
        },
    ],
}


def get_destinations(db):
    destinations = db.query(Destination).all()
    return {destination.name: destination for destination in destinations}


def seed_hotels(db, destinations):
    for destination_name, hotels in HOTELS.items():
        destination = destinations[destination_name]

        for data in hotels:
            existing = (
                db.query(Hotel)
                .filter(
                    Hotel.destination_id == destination.id,
                    Hotel.name == data["name"],
                )
                .first()
            )

            if existing:
                continue

            db.add(
                Hotel(
                    destination_id=destination.id,
                    latitude=destination.latitude,
                    longitude=destination.longitude,
                    **data,
                )
            )


def seed_attractions(db, destinations):
    for destination_name, attractions in ATTRACTIONS.items():
        destination = destinations[destination_name]

        for (
            name,
            _category,
            description,
            duration,
            rating,
            latitude,
            longitude,
        ) in attractions:
            existing = (
                db.query(Attraction)
                .filter(
                    Attraction.destination_id == destination.id,
                    Attraction.name == name,
                )
                .first()
            )

            if existing:
                continue

            db.add(
                Attraction(
                    destination_id=destination.id,
                    name=name,
                    description=description,
                    latitude=Decimal(str(latitude)),
                    longitude=Decimal(str(longitude)),
                    opening_hours={
                        "monday": "08:00-18:00",
                        "tuesday": "08:00-18:00",
                        "wednesday": "08:00-18:00",
                        "thursday": "08:00-18:00",
                        "friday": "08:00-18:00",
                        "saturday": "08:00-18:00",
                        "sunday": "08:00-18:00",
                    },
                    entry_fee=Decimal("5.00"),
                    duration_hours=Decimal(str(duration)),
                    rating=Decimal(str(rating)),
                )
            )


def seed_restaurants(db, destinations):
    for destination_name, restaurants in RESTAURANTS.items():
        destination = destinations[destination_name]

        for name, cuisine, cost, rating in restaurants:
            existing = (
                db.query(Restaurant)
                .filter(
                    Restaurant.destination_id == destination.id,
                    Restaurant.name == name,
                )
                .first()
            )

            if existing:
                continue

            db.add(
                Restaurant(
                    destination_id=destination.id,
                    name=name,
                    latitude=destination.latitude,
                    longitude=destination.longitude,
                    cuisine_type=cuisine,
                    avg_meal_cost=cost,
                    operating_hours={
                        "monday": "10:00-22:00",
                        "tuesday": "10:00-22:00",
                        "wednesday": "10:00-22:00",
                        "thursday": "10:00-22:00",
                        "friday": "10:00-22:00",
                        "saturday": "10:00-22:00",
                        "sunday": "10:00-22:00",
                    },
                    rating=Decimal(str(rating)),
                )
            )


def seed_events(db, destinations):
    for destination_name, events in EVENTS.items():
        destination = destinations[destination_name]

        for data in events:
            existing = (
                db.query(LocalEvent)
                .filter(
                    LocalEvent.destination_id == destination.id,
                    LocalEvent.name == data["name"],
                )
                .first()
            )

            if existing:
                continue

            db.add(
                LocalEvent(
                    destination_id=destination.id,
                    latitude=destination.latitude,
                    longitude=destination.longitude,
                    duration_hours=Decimal("3.00"),
                    **data,
                )
            )


def seed_tourism():
    db = SessionLocal()

    try:
        destinations = get_destinations(db)

        required = {"Kandy", "Colombo", "Galle"}
        missing = required - set(destinations)

        if missing:
            raise RuntimeError(
                f"Missing required destinations: {', '.join(sorted(missing))}"
            )

        seed_hotels(db, destinations)
        seed_attractions(db, destinations)
        seed_restaurants(db, destinations)
        seed_events(db, destinations)

        db.commit()

        print("Tourism seed data inserted successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_tourism()