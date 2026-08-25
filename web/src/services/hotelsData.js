// Mock data for the admin Hotels list. Field names match the real
// backend/app/schemas/tourism.py HotelResponse (name, description,
// price_per_night, facilities, rating) as of the C3.6 field audit —
// price_per_night was previously the camelCase pricePerNight, which
// violated docs/api-contract.md's snake_case rule; fixed here. The value
// is still a display range string, not the backend's single Decimal —
// adapting that is C4's job. `destination` (name, not destination_id FK)
// and `tier` (no backend field at all) are known, flagged gaps — see
// attractionsData.js for the fuller explanation, same reasoning applies.
const hotels = [
  {
    id: "hotel-98-acres",
    name: "98 Acres Resort & Spa",
    destination: "Ella",
    tier: "Luxury",
    rating: 4.9,
    description:
      "Sprawling hilltop resort on a working tea estate with plunge-pool villas and panoramic Ella Gap views.",
    price_per_night: "LKR 28,000–55,000",
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
    price_per_night: "LKR 35,000–65,000",
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
    price_per_night: "LKR 45,000–90,000",
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
    price_per_night: "LKR 120,000–220,000",
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
    price_per_night: "LKR 38,000–72,000",
    facilities: ["Infinity pool", "Ocean views", "Restaurant", "Yoga", "Bar"],
  },
];

export default hotels;
