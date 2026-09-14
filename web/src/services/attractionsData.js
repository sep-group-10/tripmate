// Mock data for the admin Attractions list. Field names match the real
// backend/app/schemas/tourism.py AttractionResponse (name, description,
// opening_hours, entry_fee, duration_hours, rating) as of the C3.6 field
// audit, though values here stay display strings rather than the backend's
// dict/Decimal types — adapting those is C4's job when the real API lands.
// Two fields have NO backend equivalent (flagged, not silently invented
// away): `destination` is the destination's name, not its destination_id
// FK — converting every entity to ID references + name lookups is a real
// architecture change out of scope for this mock; `category` has no
// backend field at all, it's a client-side taxonomy for filtering/display.
const attractions = [
  {
    id: "attr-nine-arch-bridge",
    name: "Nine Arch Bridge",
    destination: "Ella",
    category: "Historical",
    rating: 4.9,
    description:
      "A stunning colonial-era viaduct built in 1921 without steel — best viewed as a train passes over the jungle canopy.",
    opening_hours: "All day",
    entry_fee: "Free",
    duration_hours: "1–2 hr",
  },
  {
    id: "attr-ella-rock",
    name: "Ella Rock Hike",
    destination: "Ella",
    category: "Hiking",
    rating: 4.8,
    description:
      "A challenging jungle trail rewarding hikers with sweeping panoramas of Ella Gap and surrounding tea estates.",
    opening_hours: "Dawn–Dusk",
    entry_fee: "Free",
    duration_hours: "4–5 hr",
  },
  {
    id: "attr-temple-of-the-tooth",
    name: "Temple of the Tooth Relic",
    destination: "Kandy",
    category: "Religious",
    rating: 4.9,
    description:
      "Sri Lanka's most sacred Buddhist site, believed to house the left canine tooth of the Buddha, drawn by thousands daily.",
    opening_hours: "5:30–20:00",
    entry_fee: "LKR 1,500",
    duration_hours: "2 hr",
  },
  {
    id: "attr-botanic-gardens",
    name: "Royal Botanic Gardens Peradeniya",
    destination: "Kandy",
    category: "Nature",
    rating: 4.7,
    description:
      "A 147-acre botanical garden with a 350-year-old Java fig tree, orchid house, and dramatic river loop.",
    opening_hours: "7:30–17:30",
    entry_fee: "LKR 2,500",
    duration_hours: "2–3 hr",
  },
  {
    id: "attr-sigiriya-rock",
    name: "Sigiriya Rock Fortress",
    destination: "Sigiriya",
    category: "Historical",
    rating: 4.9,
    description:
      "A fifth-century palace atop a 200m granite monolith, with frescoes, mirror wall and water gardens below.",
    opening_hours: "7:00–17:30",
    entry_fee: "USD 30",
    duration_hours: "3–4 hr",
  },
  {
    id: "attr-minneriya",
    name: "Minneriya National Park",
    destination: "Sigiriya",
    category: "Nature",
    rating: 4.8,
    description:
      "Home to The Gathering — hundreds of wild elephants converging on the reservoir in the dry season.",
    opening_hours: "6:00–18:00",
    entry_fee: "USD 25",
    duration_hours: "3 hr",
  },
];

export default attractions;
