from app.core.seed_data._helpers import hours

DESTINATION = {
    "name": "Galle",
    "description": (
        "A historic coastal city in the Southern Province, famous for "
        "Galle Fort, colonial architecture, beaches, and cultural attractions."
    ),
    "country": "Sri Lanka",
    "region": "Southern Province",
    "latitude": 6.0535,
    "longitude": 80.2210,
    "is_active": True,
    "attractions": [
        {
            "name": "Galle Fort",
            "description": (
                "UNESCO-listed historic fortification overlooking the Indian Ocean."
            ),
            "latitude": 6.0329,
            "longitude": 80.2168,
            "entry_fee": 0.00,
            "duration_hours": 3.0,
            "rating": 4.9,
            "opening_hours": hours("06:00-20:00"),
        },
        {
            "name": "Dutch Reformed Church",
            "description": "Historic church located inside Galle Fort.",
            "latitude": 6.0285,
            "longitude": 80.2166,
            "entry_fee": 0.00,
            "duration_hours": 1.0,
            "rating": 4.4,
            "opening_hours": hours("09:00-17:00"),
        },
        {
            "name": "Galle Lighthouse",
            "description": "Historic lighthouse overlooking the southern coastline.",
            "latitude": 6.0269,
            "longitude": 80.2182,
            "entry_fee": 0.00,
            "duration_hours": 1.0,
            "rating": 4.7,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Jungle Beach",
            "description": "Secluded beach surrounded by tropical vegetation.",
            "latitude": 6.0140,
            "longitude": 80.2460,
            "entry_fee": 0.00,
            "duration_hours": 3.0,
            "rating": 4.6,
            "opening_hours": hours("07:00-18:00"),
        },
        {
            "name": "Unawatuna Beach",
            "description": (
                "Popular sandy beach known for swimming and coastal scenery."
            ),
            "latitude": 6.0090,
            "longitude": 80.2490,
            "entry_fee": 0.00,
            "duration_hours": 3.0,
            "rating": 4.7,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Martin Wickramasinghe Museum",
            "description": (
                "Museum dedicated to Sri Lankan writer Martin Wickramasinghe."
            ),
            "latitude": 5.9930,
            "longitude": 80.3290,
            "entry_fee": 4.00,
            "duration_hours": 1.5,
            "rating": 4.3,
            "opening_hours": hours("08:30-17:00"),
        },
        {
            "name": "National Maritime Museum",
            "description": "Museum covering the maritime history of Galle.",
            "latitude": 6.0276,
            "longitude": 80.2170,
            "entry_fee": 4.00,
            "duration_hours": 2.0,
            "rating": 4.4,
            "opening_hours": hours("09:00-17:00"),
        },
        {
            "name": "Japanese Peace Pagoda",
            "description": "White Buddhist pagoda located on Rumassala Hill.",
            "latitude": 6.0110,
            "longitude": 80.2470,
            "entry_fee": 0.00,
            "duration_hours": 1.5,
            "rating": 4.7,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Rumassala Forest",
            "description": "Forest area with walking trails and coastal views.",
            "latitude": 6.0120,
            "longitude": 80.2440,
            "entry_fee": 0.00,
            "duration_hours": 3.0,
            "rating": 4.5,
            "opening_hours": hours("06:00-18:00"),
        },
        {
            "name": "Koggala Lake",
            "description": (
                "Scenic lagoon offering boat rides and wildlife experiences."
            ),
            "latitude": 5.9970,
            "longitude": 80.3200,
            "entry_fee": 15.00,
            "duration_hours": 3.0,
            "rating": 4.6,
            "opening_hours": hours("07:00-17:00"),
        },
    ],
    "hotels": [
        {
            "name": "Galle Fort Budget Stay",
            "description": (
                "Affordable accommodation close to the historic Galle Fort."
            ),
            "latitude": 6.0300,
            "longitude": 80.2175,
            "price_per_night": 38.00,
            "facilities": ["WiFi", "Breakfast", "Air Conditioning"],
            "rating": 4.0,
        },
        {
            "name": "Southern Coast Hotel",
            "description": (
                "Comfortable hotel near Galle's beaches and historic attractions."
            ),
            "latitude": 6.0420,
            "longitude": 80.2190,
            "price_per_night": 72.00,
            "facilities": ["WiFi", "Restaurant", "Parking", "Breakfast"],
            "rating": 4.2,
        },
        {
            "name": "Galle Heritage Residence",
            "description": (
                "Stylish accommodation inspired by the historic architecture of Galle."
            ),
            "latitude": 6.0320,
            "longitude": 80.2150,
            "price_per_night": 125.00,
            "facilities": ["WiFi", "Restaurant", "Garden", "Breakfast"],
            "rating": 4.5,
        },
        {
            "name": "Ocean Breeze Galle",
            "description": "Upscale coastal hotel with relaxing ocean views.",
            "latitude": 6.0200,
            "longitude": 80.2330,
            "price_per_night": 180.00,
            "facilities": ["WiFi", "Pool", "Restaurant", "Spa", "Sea View"],
            "rating": 4.6,
        },
        {
            "name": "Galle Fort Luxury Retreat",
            "description": (
                "Premium accommodation combining colonial character with modern luxury."
            ),
            "latitude": 6.0305,
            "longitude": 80.2160,
            "price_per_night": 240.00,
            "facilities": [
                "WiFi",
                "Pool",
                "Spa",
                "Fine Dining",
                "Gym",
                "Concierge",
            ],
            "rating": 4.9,
        },
    ],
    "restaurants": [
        {
            "name": "Galle Spice House",
            "description": (
                "Family-run restaurant serving Sri Lankan rice and curry from "
                "breakfast through dinner."
            ),
            "latitude": 6.0345,
            "longitude": 80.2150,
            "cuisine_type": "Local Sri Lankan",
            "avg_meal_cost": 13.00,
            "rating": 4.6,
            "operating_hours": hours("08:00-21:00"),
        },
        {
            "name": "Galle Indian Garden",
            "description": (
                "Garden restaurant with North Indian curries, dosas and tandoor "
                "specialities."
            ),
            "latitude": 6.0495,
            "longitude": 80.2200,
            "cuisine_type": "Indian",
            "avg_meal_cost": 16.00,
            "rating": 4.4,
            "operating_hours": hours("11:00-22:00"),
        },
        {
            "name": "Fort Chinese Kitchen",
            "description": (
                "Casual restaurant inside the fort serving Chinese stir-fries "
                "and noodle dishes."
            ),
            "latitude": 6.0310,
            "longitude": 80.2165,
            "cuisine_type": "Chinese",
            "avg_meal_cost": 18.00,
            "rating": 4.2,
            "operating_hours": hours("11:30-22:30"),
        },
        {
            "name": "Fort Western Bistro",
            "description": (
                "Stylish fort bistro with pasta, steaks and a good wine list."
            ),
            "latitude": 6.0295,
            "longitude": 80.2155,
            "cuisine_type": "Western",
            "avg_meal_cost": 24.00,
            "rating": 4.5,
            "operating_hours": hours("12:00-23:00"),
        },
        {
            "name": "Southern Coast Seafood",
            "description": (
                "Evening seafood restaurant on the coast, serving the day's catch "
                "grilled or curried."
            ),
            "latitude": 6.0225,
            "longitude": 80.2255,
            "cuisine_type": "Seafood",
            "avg_meal_cost": 30.00,
            "rating": 4.7,
            "operating_hours": hours("17:00-22:30"),
        },
    ],
    "events": [
        {
            "name": "Galle Fort Heritage Festival",
            "description": (
                "Day-long festival of colonial-era heritage walks, music and "
                "craft stalls inside Galle Fort."
            ),
            "latitude": 6.0312,
            "longitude": 80.2178,
            "entry_fee": 7.00,
            "rating": 4.5,
            "days_ahead": 65,
            "duration_days": 1,
            "start_time": "10:00",
            "end_time": "20:00",
        },
        {
            "name": "Southern Coast Seafood Festival",
            "description": (
                "Seafood food festival by the harbour with cooking "
                "demonstrations and live music."
            ),
            "latitude": 6.0360,
            "longitude": 80.2130,
            "entry_fee": 10.00,
            "rating": 4.4,
            "days_ahead": 170,
            "duration_days": 1,
            "start_time": "12:00",
            "end_time": "21:00",
        },
    ],
    # Duplicate Nine Arch Bridge row created under Galle; the bridge belongs
    # to Ella (see ella.py).
    "deactivate_attractions": ["Nine Arches Bridge"],
}
