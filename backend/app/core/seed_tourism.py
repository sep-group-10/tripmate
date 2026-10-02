from datetime import date
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
                "Upscale hotel offering comfortable rooms and panoramic mountain views."
            ),
            "price_per_night": Decimal("165.00"),
            "facilities": ["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
            "rating": Decimal("4.6"),
        },
        {
            "name": "Cinnamon Grand Kandy Retreat",
            "description": (
                "Luxury-style accommodation with premium facilities and elegant rooms."
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
                "Premium accommodation combining colonial character with modern luxury."
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


# Photos uploaded through the admin endpoints (app/services/image_upload.py) live in
# S3 and are served through CloudFront. Each map is name -> object key; a record with
# no entry seeds with no photos. Note: seeding skips records that already exist, so
# these only apply to freshly seeded databases.
PHOTO_CDN = "https://de15w1uh6f0g9.cloudfront.net"

ATTRACTION_PHOTOS = {
    "Ambuluwawa Tower": (
        "places/attractions/bae2aa8d-b777-4d00-9411-423b94de40f4/fd2025f2-722d-46fa-a2c2-2aeba716e7f5.jpg"  # Wikimedia Commons: Ambuluwawa tower top.jpg
    ),
    "Bahirawakanda Temple": (
        "places/attractions/c9a01919-8ba7-4a27-9bdc-76b19294a15d/7dfc4488-4a80-48b2-82f1-ba01d1819e0c.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Bolgoda Lake": (
        "places/attractions/909ffacf-3efc-4eeb-9f4a-6a37106fa68c/f775a1aa-9923-43da-b576-7a9c420755f8.jpg"  # Wikimedia Commons: Bolgoda Lake, Sri Lanka.jpg
    ),
    "Colombo National Museum": (
        "places/attractions/2ec3428f-c50b-4367-a4df-bae4cef56f3c/e3ada087-3b80-417c-a1be-91eef9acda12.jpg"  # Wikimedia Commons: SL Colombo asv2020-01 img10 National Museum.jpg
    ),
    "Galle Face Green": (
        "places/attractions/aa0f443d-4cbc-45d7-a0bc-013f1e32ab1a/98dfbfc1-b879-414b-95c5-8fb08975e21b.jpg"  # Wikimedia Commons: Galle Face Green - sunset.jpg
    ),
    "Gangaramaya Temple": (
        "places/attractions/750a9bad-d991-46f2-94fa-23af46b8c1fa/4df19978-5232-47cd-9796-c2d17f521cda.jpg"  # Wikimedia Commons: Colombo Temple bouddhiste de Gangaramaya (2).JPG
    ),
    "Independence Memorial Hall": (
        "places/attractions/b5659692-e8c8-4629-8267-1301926c0bc0/be7c126f-9b46-42b8-903d-e12f0f4c83f5.jpg"  # Wikimedia Commons: Independence Commemoration Hall.jpg
    ),
    "Jami Ul-Alfar Mosque": (
        "places/attractions/7934fdf8-c3fa-4d09-a56c-31f5e4f9f643/8b7106ce-63df-450e-b065-4b4402d0f14a.jpg"  # Wikimedia Commons: SL Colombo asv2020-01 img22 Jami Ul-Alfar Mosque.jpg
    ),
    "Jungle Beach": (
        "places/attractions/bd1d2af9-cdfa-4812-ba1b-e00055f6125e/559384e1-183c-4492-8870-4495586e0df5.jpg"  # Wikimedia Commons: Jungle beach Galle.jpg
    ),
    "Kandy Cultural Dance Centre": (
        "places/attractions/376bde72-c51d-4b35-897d-fc438315161f/7ab9770b-574c-425e-bd4f-d9210f091d12.jpg"  # Wikimedia Commons: Kandyan dance performance at Kandyan Cultural Centre, Sangar
    ),
    "Kandy Lake": (
        "places/attractions/6c8a5f05-7cf8-475b-8019-fe593de53680/c5887e03-f0ec-4f35-b975-afc67bc7a75f.jpg"  # Wikimedia Commons: Island of Kandy lake.JPG
    ),
    "Kandy National Museum": (
        "places/attractions/e119086a-c1df-40a3-8192-20044d1d32fe/3b6f48f6-a3d4-4796-8be0-86cf1c648630.jpg"  # Wikimedia Commons: Kandy National Museum.jpg
    ),
    "Knuckles Mountain Range": (
        "places/attractions/16e5b438-9545-4373-a17c-36dbfcfc903d/ed0123ab-8ca3-4e3c-98b8-948aa754e854.jpg"  # Wikimedia Commons: Knuckles Mountain Range 5.jpg
    ),
    "Koggala Lake": (
        "places/attractions/ae069b68-100d-4178-8b71-6a1e1e530d87/aea0e54c-7afa-4ddf-8652-db2a0c174e71.jpg"  # Wikimedia Commons: Lake Koggala mangroves.jpg
    ),
    "Mount Lavinia Beach": (
        "places/attractions/f5649a0b-b2d4-450d-b72e-84149a4b6b4a/eccb4e89-a9df-4f6e-b3cb-81a370d0b19c.jpg"  # Wikimedia Commons: Mount Lavinia Hotel Beach.jpg
    ),
    "Rumassala Forest": (
        "places/attractions/f9962183-fb3f-42f7-bd91-7c18b532b320/2a125e64-bfba-4458-b736-a4140eefd0e6.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Temple of the Sacred Tooth Relic": (
        "places/attractions/eb4d4adb-9cb8-43df-8132-36e5b3720ccc/cd36fb69-f95f-4760-b645-43ff0fdb0f3b.jpg"  # Wikimedia Commons: SL Kandy asv2020-01 img34 Sacred Tooth Temple.jpg
    ),
    "Udawattakele Forest Reserve": (
        "places/attractions/761ce090-72ef-4c28-bb34-910fcab84858/fa93fc76-0041-4b46-af6b-08a3d01ca327.jpg"  # Wikimedia Commons: White-Browed Fantail in Udawatta Kele Animal Sanctuary.jpg
    ),
    "Unawatuna Beach": (
        "places/attractions/bda7003f-79a2-4943-869d-64712252c77e/8fdabfda-6edb-4ad6-9bf8-e710d92a478e.jpg"  # Wikimedia Commons: Unawatuna.jpg
    ),
    "Viharamahadevi Park": (
        "places/attractions/6cd42dc3-184b-4321-8ef7-50a4b65f076f/0631f232-be91-498d-8782-f9c3f2927db7.jpg"  # Wikimedia Commons: SL Colombo asv2020-01 img11 Viharamahadevi Park.jpg
    ),
}

HOTEL_PHOTOS = {
    "Cinnamon Grand Kandy Retreat": (
        "places/hotels/303b652f-f444-4c0c-9683-fc1ce15b80b5/c89b4ee5-e981-4820-8566-1568a3abcbf0.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Colombo Grand Palace": (
        "places/hotels/7ef5c1b2-2319-4fc1-9feb-2b4133c2838c/9ca69b5c-a23c-4b63-b117-e1efc3a9e19d.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Galle Fort Budget Stay": (
        "places/hotels/8c4c6990-9e32-48f7-be69-64ea385d6a97/3874df47-2ad1-4824-86d2-ee26182de718.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Galle Fort Luxury Retreat": (
        "places/hotels/bc5eca81-f032-4ed2-bbf9-a6be530a0077/6df38ede-dc57-4684-9e3d-5f75b4781275.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Kandy Heritage Hotel": (
        "places/hotels/cfa90c5a-c44e-4e9e-bf31-a0507e29aa4d/b927facf-adb4-4959-836d-ecf3f3902c6e.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Ocean Breeze Galle": (
        "places/hotels/4adbd2e6-9af9-4f95-bc08-83acc30b39ae/4129d18d-ef34-48de-b68e-06cba0791dde.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Ocean View Colombo": (
        "places/hotels/af9d95b8-6ed2-450f-ae4e-4455350eefb7/f69e5c8b-7942-4c67-bc6a-247a351c0b72.jpg"  # Wikimedia Commons: Beautiful Sunrise over the Colombo Skyline as seen from the
    ),
}

RESTAURANT_PHOTOS = {
    "Colombo Dragon Palace": (
        "places/restaurants/35a6d736-afa3-4254-baa8-eb7b7f45b0bc/53f553fb-6e8c-481b-8e18-2639e39e9382.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Colombo Heritage Kitchen": (
        "places/restaurants/b013fe72-ae89-40af-bd71-f9c97eee5931/519ca8ea-924e-4366-98e9-35329b0c8575.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Colombo Seafood Harbour": (
        "places/restaurants/abd01748-2aa6-406a-bdd9-259f8ffcffb9/01b3b8aa-ede2-4bdd-8e41-e3b9b92aecdd.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Fort Western Bistro": (
        "places/restaurants/08d43242-5708-4c15-96cc-c179bea424e0/2669360a-5343-4fc7-b2c2-3749f2b633cd.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Galle Indian Garden": (
        "places/restaurants/5eda1648-8e83-404b-a6bc-add4e482f288/293c5d29-8ef2-45d2-aaf2-484d758aa9b1.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Galle Spice House": (
        "places/restaurants/eadcfb20-6f03-4a83-b356-c1b7eb105fe8/583f9e60-a2ca-4120-af62-dd32f23f7c2e.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Hilltop Western Bistro": (
        "places/restaurants/06ce21dc-089e-4389-9092-d2ae8e409f2d/bc092981-733d-43f2-9ea6-05c486b9d617.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Kandy Indian Kitchen": (
        "places/restaurants/e1df93b9-a9cb-4616-b644-bd6330e07445/20d782e4-e72e-4d87-a19e-5b2e4f1ea259.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Kandy Lake Seafood House": (
        "places/restaurants/06abda08-a80a-4da8-90c7-a409592bdde5/564f3814-3fcf-47b9-a390-fdbe1601e0b9.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Ocean Terrace Bistro": (
        "places/restaurants/817c0c77-8294-4e34-b4ee-ff667aabd73e/7b759f3c-1b04-4456-bb21-13d6e3903487.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Pettah Indian Restaurant": (
        "places/restaurants/aa5e242b-ef36-491f-a436-dedb0e14956c/cd1b0946-b01b-4e72-9a83-40eb6e7bb573.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
}

EVENT_PHOTOS = {
    "Colombo Coastal Music Festival": (
        "places/local-events/38aa157c-aa2d-4d83-a99b-541730df754c/7286332b-f65f-493b-98a8-7a398b227db2.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Colombo Food and Culture Fair": (
        "places/local-events/636b6e62-0cbf-4109-85b8-cb3e4948aef9/62de7ea0-8f21-4bf7-90ab-a17519e27d63.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Galle Fort Heritage Festival": (
        "places/local-events/2c5c4418-c0da-443e-93a7-84434b9c2ee3/0d390c0d-a593-4b8a-b0dc-df6094b7929d.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Kandy Traditional Arts Exhibition": (
        "places/local-events/cabf2609-c744-4b00-9b59-d3d007a8cf63/47b66d6b-77b2-46ee-95f3-19ce963dc813.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
    "Southern Coast Seafood Festival": (
        "places/local-events/a3ebb216-af0f-4141-8a2e-d97b868e1c02/3ea294eb-915b-43f0-8d22-cb4047b3450f.jpg"  # placeholder photo (picsum), replace with a relevant one
    ),
}

# PENDING FIX - deliberately NOT listed above because the photo currently in the
# dev database is a wrong or doubtful match. These seed with no photo until a
# correct one is uploaded and added to the maps:
#   attractions: Colombo Fort - matched Fort railway station only
#   attractions: Colombo Lotus Tower - unverified (Blue lotus tower)
#   attractions: Dutch Reformed Church - matched a church in Winburg, South Africa
#   attractions: Galle Fort - same image as Galle Lighthouse
#   attractions: Galle Lighthouse - same image as Galle Fort
#   attractions: Japanese Peace Pagoda - matched a hostel entrance
#   attractions: Martin Wickramasinghe Museum - unverified (Great Author's Place)
#   attractions: National Maritime Museum - matched the Australian museum in Sydney
#   attractions: Nine Arch Bridge - unverified (Demodara img02)
#   attractions: Royal Botanical Gardens - matched Kew Gardens, London
#   attractions: World Buddhist Museum - matched an unrelated Qing statue
#   hotels: Colombo Central Hotel - matched Christchurch NZ panorama
#   hotels: Colombo City Budget Hotel - matched Christchurch NZ panorama
#   hotels: Galle Heritage Residence - matched a castle courtyard, not Galle
#   hotels: Hill View Kandy - matched a viewpoint, not a hotel
#   hotels: Kandy Lake Residence - shares its image with Royal Hills Kandy
#   hotels: Marina Colombo - matched an Italian marina
#   hotels: Royal Hills Kandy - shares its image with Kandy Lake Residence
#   hotels: Southern Coast Hotel - matched Dubrovnik, Croatia
#   restaurants: Fort Chinese Kitchen - matched a Hong Kong restaurant
#   restaurants: Kandy Spice Garden - matched palms in a botanical garden
#   restaurants: Lake View Chinese Restaurant - matched a restaurant in Florida
#   restaurants: Southern Coast Seafood - matched an unrelated 1979 coast photo
#   events: Kandy Cultural Heritage Festival - unverified (Kandy - 55326621499)


def _photo_urls(photos, name):
    key = photos.get(name)
    return [f"{PHOTO_CDN}/{key}"] if key else None


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
                    photo_urls=_photo_urls(HOTEL_PHOTOS, data["name"]),
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
                    photo_urls=_photo_urls(ATTRACTION_PHOTOS, name),
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
                    photo_urls=_photo_urls(RESTAURANT_PHOTOS, name),
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

            event_date = date.fromisoformat(data["event_schedule"]["date"])

            db.add(
                LocalEvent(
                    destination_id=destination.id,
                    latitude=destination.latitude,
                    longitude=destination.longitude,
                    duration_hours=Decimal("3.00"),
                    starts_on=event_date,
                    ends_on=event_date,
                    photo_urls=_photo_urls(EVENT_PHOTOS, data["name"]),
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
