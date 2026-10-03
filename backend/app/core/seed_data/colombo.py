from app.core.seed_data._helpers import hours

DESTINATION = {
    "name": "Colombo",
    "description": (
        "Sri Lanka's commercial capital, offering a mix of modern city life, "
        "colonial architecture, coastal attractions, shopping, and dining."
    ),
    "country": "Sri Lanka",
    "region": "Western Province",
    "latitude": 6.9271,
    "longitude": 79.8612,
    "is_active": True,
    "attractions": [
        {
            "name": "Gangaramaya Temple",
            "description": (
                "Historic Buddhist temple featuring religious and cultural collections."
            ),
            "latitude": 6.9167,
            "longitude": 79.8560,
            "entry_fee": 3.00,
            "duration_hours": 2.0,
            "rating": 4.6,
            "opening_hours": hours("06:00-20:00"),
        },
        {
            "name": "Jami Ul-Alfar Mosque",
            "description": "Distinctive historic mosque in the Pettah area.",
            "latitude": 6.9369,
            "longitude": 79.8500,
            "entry_fee": 0.00,
            "duration_hours": 1.0,
            "rating": 4.4,
            "opening_hours": hours("08:00-17:00"),
        },
        {
            "name": "Galle Face Green",
            "description": "Popular seaside promenade ideal for sunset walks.",
            "latitude": 6.9271,
            "longitude": 79.8436,
            "entry_fee": 0.00,
            "duration_hours": 2.0,
            "rating": 4.5,
            "opening_hours": hours("06:00-22:00"),
        },
        {
            "name": "Viharamahadevi Park",
            "description": "Large public park in central Colombo.",
            "latitude": 6.9147,
            "longitude": 79.8612,
            "entry_fee": 0.00,
            "duration_hours": 2.0,
            "rating": 4.4,
            "opening_hours": hours("06:00-19:00"),
        },
        {
            "name": "Colombo National Museum",
            "description": (
                "Major museum documenting Sri Lanka's history and heritage."
            ),
            "latitude": 6.9107,
            "longitude": 79.8587,
            "entry_fee": 5.00,
            "duration_hours": 2.5,
            "rating": 4.6,
            "opening_hours": hours("09:00-17:00"),
        },
        {
            "name": "Colombo Fort",
            "description": (
                "Historic commercial district containing colonial-era buildings."
            ),
            "latitude": 6.9344,
            "longitude": 79.8428,
            "entry_fee": 0.00,
            "duration_hours": 2.0,
            "rating": 4.3,
            "opening_hours": hours("06:00-20:00"),
        },
        {
            "name": "Independence Memorial Hall",
            "description": (
                "National monument commemorating Sri Lanka's independence."
            ),
            "latitude": 6.9057,
            "longitude": 79.8692,
            "entry_fee": 0.00,
            "duration_hours": 1.5,
            "rating": 4.5,
            "opening_hours": hours("08:00-18:00"),
        },
        {
            "name": "Colombo Lotus Tower",
            "description": ("Iconic communications tower with observation facilities."),
            "latitude": 6.9272,
            "longitude": 79.8584,
            "entry_fee": 20.00,
            "duration_hours": 2.0,
            "rating": 4.6,
            "opening_hours": hours("09:00-21:00"),
        },
        {
            "name": "Bolgoda Lake",
            "description": "Large lake offering boating and outdoor activities.",
            "latitude": 6.7780,
            "longitude": 79.9200,
            "entry_fee": 15.00,
            "duration_hours": 3.0,
            "rating": 4.4,
            "opening_hours": hours("07:00-18:00"),
        },
        {
            "name": "Mount Lavinia Beach",
            "description": (
                "Popular beach suitable for swimming and coastal activities."
            ),
            "latitude": 6.8344,
            "longitude": 79.8637,
            "entry_fee": 0.00,
            "duration_hours": 3.0,
            "rating": 4.5,
            "opening_hours": hours("06:00-18:00"),
        },
    ],
    "hotels": [
        {
            "name": "Colombo City Budget Hotel",
            "description": (
                "Affordable accommodation close to shopping and city attractions."
            ),
            "latitude": 6.9360,
            "longitude": 79.8540,
            "price_per_night": 35.00,
            "facilities": ["WiFi", "Breakfast", "Air Conditioning"],
            "rating": 4.0,
        },
        {
            "name": "Ocean View Colombo",
            "description": (
                "Comfortable mid-range hotel overlooking the Colombo coastline."
            ),
            "latitude": 6.9120,
            "longitude": 79.8480,
            "price_per_night": 78.00,
            "facilities": ["WiFi", "Restaurant", "Sea View", "Breakfast"],
            "rating": 4.2,
        },
        {
            "name": "Colombo Central Hotel",
            "description": (
                "Modern hotel convenient for business travellers and tourists."
            ),
            "latitude": 6.9200,
            "longitude": 79.8650,
            "price_per_night": 110.00,
            "facilities": ["WiFi", "Restaurant", "Gym", "Room Service"],
            "rating": 4.4,
        },
        {
            "name": "Marina Colombo",
            "description": "Upscale coastal hotel with modern rooms and city views.",
            "latitude": 6.8930,
            "longitude": 79.8540,
            "price_per_night": 175.00,
            "facilities": ["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
            "rating": 4.6,
        },
        {
            "name": "Colombo Grand Palace",
            "description": (
                "Luxury city hotel with premium dining and wellness facilities."
            ),
            "latitude": 6.9330,
            "longitude": 79.8450,
            "price_per_night": 260.00,
            "facilities": [
                "WiFi",
                "Spa",
                "Pool",
                "Fine Dining",
                "Gym",
                "Concierge",
            ],
            "rating": 4.8,
        },
    ],
    "restaurants": [
        {
            "name": "Colombo Heritage Kitchen",
            "description": (
                "Traditional Sri Lankan rice and curry served in a colonial-style "
                "dining room."
            ),
            "latitude": 6.9150,
            "longitude": 79.8530,
            "cuisine_type": "Local Sri Lankan",
            "avg_meal_cost": 14.00,
            "rating": 4.6,
            "operating_hours": hours("11:00-22:00"),
        },
        {
            "name": "Pettah Indian Restaurant",
            "description": (
                "Busy Pettah eatery known for biryani and South Indian vegetarian "
                "dishes. Closed Sundays when the market is shut."
            ),
            "latitude": 6.9390,
            "longitude": 79.8510,
            "cuisine_type": "Indian",
            "avg_meal_cost": 16.00,
            "rating": 4.3,
            "operating_hours": hours("08:00-17:00", sunday="closed"),
        },
        {
            "name": "Colombo Dragon Palace",
            "description": (
                "Long-running Chinese restaurant with Cantonese and Szechuan menus."
            ),
            "latitude": 6.9240,
            "longitude": 79.8520,
            "cuisine_type": "Chinese",
            "avg_meal_cost": 20.00,
            "rating": 4.4,
            "operating_hours": hours("11:30-23:00"),
        },
        {
            "name": "Ocean Terrace Bistro",
            "description": (
                "Seafront terrace bistro serving grills, salads and sunset cocktails."
            ),
            "latitude": 6.9185,
            "longitude": 79.8445,
            "cuisine_type": "Western",
            "avg_meal_cost": 28.00,
            "rating": 4.5,
            "operating_hours": hours("12:00-23:00"),
        },
        {
            "name": "Colombo Seafood Harbour",
            "description": (
                "Evening seafood restaurant near the harbour with crab, prawns "
                "and the catch of the day."
            ),
            "latitude": 6.9335,
            "longitude": 79.8415,
            "cuisine_type": "Seafood",
            "avg_meal_cost": 32.00,
            "rating": 4.7,
            "operating_hours": hours("17:30-23:00"),
        },
    ],
    "events": [
        {
            "name": "Colombo Food and Culture Fair",
            "description": (
                "Day-long fair of street food, regional cuisine and cultural "
                "performances on the Galle Face seafront."
            ),
            "latitude": 6.9240,
            "longitude": 79.8440,
            "entry_fee": 8.00,
            "rating": 4.3,
            "days_ahead": 40,
            "duration_days": 1,
            "start_time": "11:00",
            "end_time": "20:00",
        },
        {
            "name": "Colombo Coastal Music Festival",
            "description": (
                "Open-air evening concert series with local and international "
                "acts on the Mount Lavinia coast."
            ),
            "latitude": 6.8400,
            "longitude": 79.8640,
            "entry_fee": 15.00,
            "rating": 4.4,
            "days_ahead": 110,
            "duration_days": 1,
            "start_time": "16:00",
            "end_time": "22:00",
        },
    ],
}
