"""Wikimedia Commons photos for the tourism seed.

Real attractions get a photo of that exact place (looked up by attraction name).
Fictional hotels, restaurants and events get a generic stand-in photo chosen by
type and price level. Source, author and licence of every image are in
photo_credits.py.
"""

from app.core.seed_data.photo_credits import PHOTO_CREDITS

COMMONS_URL_PREFIX = "https://upload.wikimedia.org/"

ATTRACTION_PHOTO_URLS = {
    credit["name"]: credit["url"]
    for credit in PHOTO_CREDITS
    if credit["kind"] == "attraction"
}
GENERIC_PHOTO_URLS = {
    credit["name"]: credit["url"]
    for credit in PHOTO_CREDITS
    if credit["kind"] == "generic"
}

# Places whose photo already in the database is known to be wrong (see the
# PENDING FIX list in photos.py). A Commons/generic photo replaces these; any
# other existing photo is left alone.
KNOWN_WRONG_PHOTO_NAMES = {
    # attractions
    "Colombo Fort",
    "Colombo Lotus Tower",
    "Dutch Reformed Church",
    "Galle Fort",
    "Galle Lighthouse",
    "Japanese Peace Pagoda",
    "Martin Wickramasinghe Museum",
    "National Maritime Museum",
    "Nine Arch Bridge",
    "Royal Botanical Gardens",
    "World Buddhist Museum",
    # hotels
    "Colombo Central Hotel",
    "Colombo City Budget Hotel",
    "Galle Heritage Residence",
    "Hill View Kandy",
    "Kandy Lake Residence",
    "Marina Colombo",
    "Royal Hills Kandy",
    "Southern Coast Hotel",
    # restaurants
    "Fort Chinese Kitchen",
    "Kandy Spice Garden",
    "Lake View Chinese Restaurant",
    "Southern Coast Seafood",
    # events
    "Kandy Cultural Heritage Festival",
}

_BUDGET_MAX = 60  # price_per_night below this is a budget room
_RESORT_MIN = 150  # price_per_night from this up is a resort

_CUISINE_PHOTO = {
    "Local Sri Lankan": "rice_and_curry",
    "Seafood": "seafood",
    "Western": "cafe",
    "Indian": "indian_curry",
    "Chinese": "noodles",
}

# Checked in order; first keyword hit wins, otherwise "festival".
_EVENT_PHOTO_KEYWORDS = (
    (
        "perahera",
        ("perahera", "procession", "poya", "vesak", "lantern", "temple festival"),
    ),
    ("street_food", ("food", "fish", "seafood")),
    (
        "beach_event",
        ("beach", "coastal", "surf", "water sports", "whale", "ocean", "bonfire"),
    ),
)


def attraction_photo(name: str) -> str | None:
    return ATTRACTION_PHOTO_URLS.get(name)


def hotel_photo(hotel: dict) -> str:
    price = hotel["price_per_night"]
    if price < _BUDGET_MAX:
        return GENERIC_PHOTO_URLS["budget_room"]
    if price >= _RESORT_MIN:
        return GENERIC_PHOTO_URLS["resort_pool"]
    return GENERIC_PHOTO_URLS["midrange_room"]


def restaurant_photo(restaurant: dict) -> str:
    key = _CUISINE_PHOTO.get(restaurant["cuisine_type"], "street_food")
    return GENERIC_PHOTO_URLS[key]


def event_photo(event: dict) -> str:
    name = event["name"].lower()
    for key, keywords in _EVENT_PHOTO_KEYWORDS:
        if any(keyword in name for keyword in keywords):
            return GENERIC_PHOTO_URLS[key]
    return GENERIC_PHOTO_URLS["festival"]
