import uuid

from app.core.seed_data._helpers import hours

DESTINATION = {
    "id": uuid.UUID("83f7d353-8731-4663-8e79-1a54d473f6dd"),
    "name": "Kandy",
    "description": (
        "A cultural city in the Central Province, known for the "
        "Temple of the Sacred Tooth Relic, scenic hills, and Kandy Lake."
    ),
    "country": "Sri Lanka",
    "region": "Central Province",
    "latitude": 7.2906,
    "longitude": 80.6337,
    "is_active": True,
    "attractions": [
        {
            "name": "Temple of the Sacred Tooth Relic",
            "description": (
                "Historic Buddhist temple and one of Sri Lanka's most important "
                "religious sites."
            ),
            "latitude": 7.2937,
            "longitude": 80.6413,
            "entry_fee": 7.00,
            "duration_hours": 2.0,
            "rating": 4.9,
            "opening_hours": hours("05:30-20:00"),
        },
        {
            "name": "Kandy Lake",
            "description": "Scenic artificial lake located in the heart of Kandy.",
            "latitude": 7.2940,
            "longitude": 80.6380,
            "entry_fee": 0.00,
            "duration_hours": 1.5,
            "rating": 4.6,
            "opening_hours": hours("06:00-20:00"),
        },
        {
            "name": "Royal Botanical Gardens",
            "description": (
                "Large botanical garden famous for tropical plants and orchids."
            ),
            "latitude": 7.2697,
            "longitude": 80.5966,
            "entry_fee": 10.00,
            "duration_hours": 3.0,
            "rating": 4.7,
            "opening_hours": hours("07:30-17:00"),
        },
        {
            "name": "Bahirawakanda Temple",
            "description": "Hilltop Buddhist temple offering panoramic views of Kandy.",
            "latitude": 7.2909,
            "longitude": 80.6266,
            "entry_fee": 0.00,
            "duration_hours": 1.5,
            "rating": 4.5,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Kandy National Museum",
            "description": (
                "Museum displaying artefacts related to Kandy's royal history."
            ),
            "latitude": 7.2944,
            "longitude": 80.6412,
            "entry_fee": 3.00,
            "duration_hours": 2.0,
            "rating": 4.3,
            "opening_hours": hours("09:00-17:00"),
        },
        {
            "name": "Udawattakele Forest Reserve",
            "description": (
                "Forest reserve offering walking trails and rich biodiversity."
            ),
            "latitude": 7.3006,
            "longitude": 80.6465,
            "entry_fee": 5.00,
            "duration_hours": 3.0,
            "rating": 4.6,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Kandy Cultural Dance Centre",
            "description": (
                "Venue showcasing traditional Sri Lankan dance performances."
            ),
            "latitude": 7.2925,
            "longitude": 80.6418,
            "entry_fee": 12.00,
            "duration_hours": 1.5,
            "rating": 4.5,
            "opening_hours": hours("09:00-19:00"),
        },
        {
            "name": "World Buddhist Museum",
            "description": (
                "Museum presenting Buddhist heritage from different countries."
            ),
            "latitude": 7.2941,
            "longitude": 80.6422,
            "entry_fee": 4.00,
            "duration_hours": 2.0,
            "rating": 4.4,
            "opening_hours": hours("09:00-17:00"),
        },
        {
            "name": "Knuckles Mountain Range",
            "description": "Mountain area offering hiking and nature experiences.",
            "latitude": 7.4500,
            "longitude": 80.8000,
            "entry_fee": 10.00,
            "duration_hours": 6.0,
            "rating": 4.8,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Ambuluwawa Tower",
            "description": (
                "Unique tower surrounded by mountain scenery and hiking trails."
            ),
            "latitude": 7.1269,
            "longitude": 80.6385,
            "entry_fee": 3.00,
            "duration_hours": 3.0,
            "rating": 4.7,
            "opening_hours": hours("06:00-18:00"),
        },
    ],
    "hotels": [
        {
            "name": "Kandy Heritage Hotel",
            "description": (
                "Comfortable budget accommodation near central Kandy and Kandy Lake."
            ),
            "latitude": 7.2924,
            "longitude": 80.6350,
            "price_per_night": 42.00,
            "facilities": ["WiFi", "Breakfast", "Air Conditioning", "Parking"],
            "rating": 4.1,
        },
        {
            "name": "Hill View Kandy",
            "description": (
                "Affordable hotel with scenic views of the surrounding hills."
            ),
            "latitude": 7.2870,
            "longitude": 80.6290,
            "price_per_night": 65.00,
            "facilities": ["WiFi", "Restaurant", "Room Service", "Parking"],
            "rating": 4.2,
        },
        {
            "name": "Kandy Lake Residence",
            "description": (
                "Mid-range accommodation within easy reach of Kandy Lake "
                "and cultural attractions."
            ),
            "latitude": 7.2922,
            "longitude": 80.6402,
            "price_per_night": 95.00,
            "facilities": ["WiFi", "Restaurant", "Swimming Pool", "Breakfast"],
            "rating": 4.4,
        },
        {
            "name": "Royal Hills Kandy",
            "description": (
                "Upscale hotel offering comfortable rooms and panoramic mountain views."
            ),
            "latitude": 7.2810,
            "longitude": 80.6420,
            "price_per_night": 165.00,
            "facilities": ["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
            "rating": 4.6,
        },
        {
            "name": "Cinnamon Grand Kandy Retreat",
            "description": (
                "Luxury-style accommodation with premium facilities and elegant rooms."
            ),
            "latitude": 7.2890,
            "longitude": 80.6380,
            "price_per_night": 220.00,
            "facilities": [
                "WiFi",
                "Spa",
                "Pool",
                "Fine Dining",
                "Gym",
                "Airport Transfer",
            ],
            "rating": 4.8,
        },
    ],
    "restaurants": [
        {
            "name": "Kandy Spice Garden",
            "description": (
                "Relaxed garden restaurant serving rice and curry and other "
                "Sri Lankan home-style dishes, open for breakfast and lunch."
            ),
            "latitude": 7.2915,
            "longitude": 80.6360,
            "cuisine_type": "Local Sri Lankan",
            "avg_meal_cost": 12.00,
            "rating": 4.5,
            "operating_hours": hours("08:00-17:00"),
        },
        {
            "name": "Kandy Indian Kitchen",
            "description": (
                "North and South Indian curries, tandoor dishes and fresh breads."
            ),
            "latitude": 7.2928,
            "longitude": 80.6345,
            "cuisine_type": "Indian",
            "avg_meal_cost": 15.00,
            "rating": 4.3,
            "operating_hours": hours("11:00-22:30"),
        },
        {
            "name": "Lake View Chinese Restaurant",
            "description": (
                "Cantonese and Sri Lankan-Chinese dishes with views over Kandy Lake."
            ),
            "latitude": 7.2945,
            "longitude": 80.6368,
            "cuisine_type": "Chinese",
            "avg_meal_cost": 14.00,
            "rating": 4.2,
            "operating_hours": hours("11:30-22:00"),
        },
        {
            "name": "Hilltop Western Bistro",
            "description": (
                "Hillside bistro serving grills, pasta and desserts with city views."
            ),
            "latitude": 7.2860,
            "longitude": 80.6300,
            "cuisine_type": "Western",
            "avg_meal_cost": 22.00,
            "rating": 4.4,
            "operating_hours": hours("11:00-23:00"),
        },
        {
            "name": "Kandy Lake Seafood House",
            "description": (
                "Evening seafood restaurant near the lake, known for grilled "
                "prawns and crab curry."
            ),
            "latitude": 7.2932,
            "longitude": 80.6390,
            "cuisine_type": "Seafood",
            "avg_meal_cost": 25.00,
            "rating": 4.6,
            "operating_hours": hours("17:00-22:30"),
        },
    ],
    "events": [
        {
            "name": "Kandy Cultural Heritage Festival",
            "description": (
                "Evening celebration of Kandyan culture with drumming, dance "
                "and traditional costumes."
            ),
            "latitude": 7.2950,
            "longitude": 80.6430,
            "entry_fee": 10.00,
            "rating": 4.5,
            "days_ahead": 50,
            "duration_days": 1,
            "start_time": "18:00",
            "end_time": "21:00",
        },
        {
            "name": "Kandy Traditional Arts Exhibition",
            "description": (
                "Daytime exhibition of local crafts including lacquerware, "
                "wood carving and batik, with live demonstrations."
            ),
            "latitude": 7.2900,
            "longitude": 80.6395,
            "entry_fee": 5.00,
            "rating": 4.2,
            "days_ahead": 140,
            "duration_days": 1,
            "start_time": "10:00",
            "end_time": "17:00",
        },
    ],
    # Duplicate Nine Arch Bridge rows that were created under Kandy; the
    # bridge belongs to Ella (see ella.py).
    "deactivate_attractions": ["Nine Arch Bridge", "Nine Arches Bridge"],
}
