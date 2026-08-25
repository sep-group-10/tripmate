// Mock data for the admin Hotels list (C3.1). Field names follow
// backend/app/models/hotel.py (name, description, price_per_night,
// facilities, rating), and sample content matches the established set in
// design-reference/TripMate Admin Dashboard.dc.html (shown there as
// "Accommodations" — equivalent to "Hotels" for this issue).
const hotels = [
  {
    id: "hotel-98-acres",
    name: "98 Acres Resort & Spa",
    destination: "Ella",
    tier: "Luxury",
    rating: 4.9,
    description:
      "Sprawling hilltop resort on a working tea estate with plunge-pool villas and panoramic Ella Gap views.",
    pricePerNight: "LKR 28,000–55,000",
    facilities: [
      "Infinity pool",
      "Spa",
      "Tea plantation views",
      "Restaurant",
      "Yoga",
    ],
  },
  {
    id: "hotel-kandy-house",
    name: "The Kandy House",
    destination: "Kandy",
    tier: "Luxury",
    rating: 4.9,
    description:
      "A restored 19th-century Kandyan chieftain's manor with antique-furnished suites and a heated plunge pool amid rice paddies.",
    pricePerNight: "LKR 35,000–65,000",
    facilities: ["Pool", "Spa", "Garden", "Restaurant", "Butler service"],
  },
  {
    id: "hotel-water-garden",
    name: "Water Garden Sigiriya",
    destination: "Sigiriya",
    tier: "Luxury",
    rating: 4.8,
    description:
      "Fifteen freestanding pool villas inspired by ancient water gardens — the most romantic address in the Cultural Triangle.",
    pricePerNight: "LKR 45,000–90,000",
    facilities: [
      "Private pool villas",
      "Spa",
      "Restaurant",
      "Cultural shows",
      "Cycling",
    ],
  },
  {
    id: "hotel-amangalla",
    name: "Amangalla",
    destination: "Galle",
    tier: "Luxury",
    rating: 4.9,
    description:
      "The grandest address inside Galle Fort — a 300-year-old colonial building reimagined as an ultra-luxury sanctuary with 30 suites.",
    pricePerNight: "LKR 120,000–220,000",
    facilities: ["Spa", "Pool", "Library", "Fort views", "Tuk-tuk tours"],
  },
  {
    id: "hotel-mirissa-hills",
    name: "Mirissa Hills",
    destination: "Mirissa",
    tier: "Boutique",
    rating: 4.6,
    description:
      "Cascading clifftop villas with ocean panoramas, a hilltop infinity pool, and the best sunset bar on the southern coast.",
    pricePerNight: "LKR 38,000–72,000",
    facilities: ["Infinity pool", "Ocean views", "Restaurant", "Yoga", "Bar"],
  },
];

export default hotels;
