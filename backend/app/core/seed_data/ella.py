from app.core.seed_data._helpers import hours

# Ella is intentionally incomplete: only its signature attraction is seeded.
# Hotels, restaurants and more attractions are still to come, so it is marked
# planner_ready=False and the completeness tests skip it.
DESTINATION = {
    "name": "Ella",
    "description": "Hill country town famous for tea estates and mountain views.",
    "country": "Sri Lanka",
    "region": "Uva Province",
    "latitude": 6.8667,
    "longitude": 81.0466,
    "is_active": True,
    "planner_ready": False,
    "attractions": [
        {
            "name": "Nine Arch Bridge",
            "description": (
                "Iconic colonial-era railway viaduct between Ella and Demodara, "
                "set in tea country and best seen when a train crosses."
            ),
            "latitude": 6.8768,
            "longitude": 81.0608,
            "entry_fee": 0.00,
            "duration_hours": 1.5,
            "rating": 4.8,
            "opening_hours": hours("06:00-18:00"),
        },
    ],
    "hotels": [],
    "restaurants": [],
    "events": [],
    "deactivate_attractions": ["Nine Arches Bridge"],
}
