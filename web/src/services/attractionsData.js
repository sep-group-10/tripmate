// Mock data for the admin Attractions list (C3.1). Field names follow
// backend/app/models/attraction.py (name, description, opening_hours,
// entry_fee, duration_hours, rating), and sample content matches the
// established set in design-reference/TripMate Admin Dashboard.dc.html.
const attractions = [
  {
    id: "attr-nine-arch-bridge",
    name: "Nine Arch Bridge",
    destination: "Ella",
    category: "Historical",
    rating: 4.9,
    description:
      "A stunning colonial-era viaduct built in 1921 without steel — best viewed as a train passes over the jungle canopy.",
    hours: "All day",
    entry: "Free",
    duration: "1–2 hr",
  },
  {
    id: "attr-ella-rock",
    name: "Ella Rock Hike",
    destination: "Ella",
    category: "Hiking",
    rating: 4.8,
    description:
      "A challenging jungle trail rewarding hikers with sweeping panoramas of Ella Gap and surrounding tea estates.",
    hours: "Dawn–Dusk",
    entry: "Free",
    duration: "4–5 hr",
  },
  {
    id: "attr-temple-of-the-tooth",
    name: "Temple of the Tooth Relic",
    destination: "Kandy",
    category: "Religious",
    rating: 4.9,
    description:
      "Sri Lanka's most sacred Buddhist site, believed to house the left canine tooth of the Buddha, drawn by thousands daily.",
    hours: "5:30–20:00",
    entry: "LKR 1,500",
    duration: "2 hr",
  },
  {
    id: "attr-botanic-gardens",
    name: "Royal Botanic Gardens Peradeniya",
    destination: "Kandy",
    category: "Nature",
    rating: 4.7,
    description:
      "A 147-acre botanical garden with a 350-year-old Java fig tree, orchid house, and dramatic river loop.",
    hours: "7:30–17:30",
    entry: "LKR 2,500",
    duration: "2–3 hr",
  },
  {
    id: "attr-sigiriya-rock",
    name: "Sigiriya Rock Fortress",
    destination: "Sigiriya",
    category: "Historical",
    rating: 4.9,
    description:
      "A fifth-century palace atop a 200m granite monolith, with frescoes, mirror wall and water gardens below.",
    hours: "7:00–17:30",
    entry: "USD 30",
    duration: "3–4 hr",
  },
  {
    id: "attr-minneriya",
    name: "Minneriya National Park",
    destination: "Sigiriya",
    category: "Nature",
    rating: 4.8,
    description:
      "Home to The Gathering — hundreds of wild elephants converging on the reservoir in the dry season.",
    hours: "6:00–18:00",
    entry: "USD 25",
    duration: "3 hr",
  },
];

export default attractions;
