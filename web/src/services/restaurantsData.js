// Mock data for the admin Restaurants list. Field names match the real
// backend/app/schemas/tourism.py RestaurantResponse (name, description,
// operating_hours, cuisine_type, rating) as of the C3.6 field audit —
// `hours`/`cuisine` were renamed from earlier, non-matching names.
// `priceRange` is deliberately NOT renamed to avg_meal_cost: the backend
// field is a single Decimal (one averaged cost), while this is a display
// range string ("LKR 2,000–5,000") — a different concept, not just a
// different type, so renaming it to avg_meal_cost would mislabel it.
// `destination` (name, not destination_id FK) is a known, flagged gap —
// see attractionsData.js for the fuller explanation.
const restaurants = [
  {
    id: "rest-cafe-chill",
    name: "Cafe Chill",
    destination: "Ella",
    cuisine_type: "International",
    rating: 4.8,
    description:
      "Rustic garden cafe with sweeping valley views, wood-fired pizzas, and live acoustic sets most evenings.",
    operating_hours: "8:00–22:00",
    priceRange: "LKR 1,200–2,800",
  },
  {
    id: "rest-empire-cafe",
    name: "The Empire Cafe",
    destination: "Kandy",
    cuisine_type: "Sri Lankan",
    rating: 4.7,
    description:
      "Colonial-era building serving hearty rice & curry buffets alongside fresh lake-view seating.",
    operating_hours: "7:00–21:00",
    priceRange: "LKR 800–1,800",
  },
  {
    id: "rest-ministry-of-crab",
    name: "Ministry of Crab",
    destination: "Colombo",
    cuisine_type: "Seafood",
    rating: 4.9,
    description:
      "Award-winning seafood restaurant inside a 400-year-old Dutch hospital, famed for jumbo lagoon crab.",
    operating_hours: "11:30–23:00",
    priceRange: "LKR 6,000–15,000",
  },
  {
    id: "rest-feast",
    name: "Feast Restaurant",
    destination: "Sigiriya",
    cuisine_type: "Sri Lankan",
    rating: 4.6,
    description:
      "Open-air dining with views of Sigiriya Rock, specialising in clay-pot curries and fresh juices.",
    operating_hours: "6:30–22:00",
    priceRange: "LKR 1,000–2,500",
  },
  {
    id: "rest-dewmini",
    name: "Dewmini Roti Shop",
    destination: "Ella",
    cuisine_type: "Street Food",
    rating: 4.5,
    description:
      "Beloved roadside stall for kottu roti and fresh juices, a favourite among backpackers and locals alike.",
    operating_hours: "9:00–21:00",
    priceRange: "LKR 300–800",
  },
  {
    id: "rest-sea-spray",
    name: "Sea Spray Restaurant",
    destination: "Galle",
    cuisine_type: "Seafood",
    rating: 4.7,
    description:
      "Rampart-side dining within Galle Fort, serving grilled catch of the day with sunset ocean views.",
    operating_hours: "12:00–22:30",
    priceRange: "LKR 2,500–5,500",
  },
];

export default restaurants;
