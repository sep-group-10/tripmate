// Mock data for the admin Destinations list (C3.1). Field names follow
// backend/app/models/destination.py (name, description, country, region,
// rating) so this lines up with the real shape once C4 wires up the API.
const destinations = [
  {
    id: "dest-kandy",
    name: "Kandy",
    region: "Central Province",
    country: "Sri Lanka",
    rating: 4.8,
    tag: "Cultural Triangle",
    description:
      "The last capital of the ancient kings, home to the Temple of the Tooth Relic and the annual Esala Perahera procession.",
  },
  {
    id: "dest-sigiriya",
    name: "Sigiriya",
    region: "Central Province",
    country: "Sri Lanka",
    rating: 4.9,
    tag: "Cultural Triangle",
    description:
      "A fifth-century rock fortress rising 200m above the jungle, with frescoes, water gardens, and sweeping views.",
  },
  {
    id: "dest-ella",
    name: "Ella",
    region: "Uva Province",
    country: "Sri Lanka",
    rating: 4.8,
    tag: "Hill Country",
    description:
      "A laid-back hill station framed by tea estates, hiking trails, and the iconic Nine Arch Bridge.",
  },
  {
    id: "dest-galle",
    name: "Galle",
    region: "Southern Province",
    country: "Sri Lanka",
    rating: 4.7,
    tag: "Coastal",
    description:
      "A UNESCO-listed Dutch colonial fort city on the southern coast, ringed by ramparts and boutique stays.",
  },
  {
    id: "dest-mirissa",
    name: "Mirissa",
    region: "Southern Province",
    country: "Sri Lanka",
    rating: 4.6,
    tag: "Coastal",
    description:
      "A crescent-shaped beach town known for whale watching, surf breaks, and clifftop sunset bars.",
  },
  {
    id: "dest-yala",
    name: "Yala National Park",
    region: "Southern Province",
    country: "Sri Lanka",
    rating: 4.7,
    tag: "Wildlife",
    description:
      "Sri Lanka's most visited national park, with one of the highest leopard densities in the world.",
  },
];

export default destinations;
