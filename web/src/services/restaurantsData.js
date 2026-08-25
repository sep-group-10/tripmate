// Mock data for the admin Restaurants list (C3.1). Field names follow
// backend/app/models/restaurant.py (name, description, operating_hours,
// cuisine_type, avg_meal_cost, rating), and sample content matches the
// established set in design-reference/TripMate Admin Dashboard.dc.html.
const restaurants = [
  {
    id: "rest-cafe-chill",
    name: "Cafe Chill",
    destination: "Ella",
    cuisine: "International",
    rating: 4.8,
    description:
      "Rustic garden cafe with sweeping valley views, wood-fired pizzas, and live acoustic sets most evenings.",
    hours: "8:00–22:00",
    priceRange: "LKR 1,200–2,800",
  },
  {
    id: "rest-empire-cafe",
    name: "The Empire Cafe",
    destination: "Kandy",
    cuisine: "Sri Lankan",
    rating: 4.7,
    description:
      "Colonial-era building serving hearty rice & curry buffets alongside fresh lake-view seating.",
    hours: "7:00–21:00",
    priceRange: "LKR 800–1,800",
  },
  {
    id: "rest-ministry-of-crab",
    name: "Ministry of Crab",
    destination: "Colombo",
    cuisine: "Seafood",
    rating: 4.9,
    description:
      "Award-winning seafood restaurant inside a 400-year-old Dutch hospital, famed for jumbo lagoon crab.",
    hours: "11:30–23:00",
    priceRange: "LKR 6,000–15,000",
  },
  {
    id: "rest-feast",
    name: "Feast Restaurant",
    destination: "Sigiriya",
    cuisine: "Sri Lankan",
    rating: 4.6,
    description:
      "Open-air dining with views of Sigiriya Rock, specialising in clay-pot curries and fresh juices.",
    hours: "6:30–22:00",
    priceRange: "LKR 1,000–2,500",
  },
  {
    id: "rest-dewmini",
    name: "Dewmini Roti Shop",
    destination: "Ella",
    cuisine: "Street Food",
    rating: 4.5,
    description:
      "Beloved roadside stall for kottu roti and fresh juices, a favourite among backpackers and locals alike.",
    hours: "9:00–21:00",
    priceRange: "LKR 300–800",
  },
  {
    id: "rest-sea-spray",
    name: "Sea Spray Restaurant",
    destination: "Galle",
    cuisine: "Seafood",
    rating: 4.7,
    description:
      "Rampart-side dining within Galle Fort, serving grilled catch of the day with sunset ocean views.",
    hours: "12:00–22:30",
    priceRange: "LKR 2,500–5,500",
  },
];

export default restaurants;
