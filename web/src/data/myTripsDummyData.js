// PLACEHOLDER DATA for the My Trips page. Nothing here comes from the
// backend: there is no GET /trips endpoint yet, Trip has no title field,
// and the chat flow never persists Itinerary/ItineraryDay rows (see
// backend/app/routers/chat.py - the day-by-day plan is returned in the
// API response only and thrown away). Replace these imports once that
// backend work lands.

export const STATS = [
  {
    label: "Trips planned",
    value: "5",
    delta: "+2 this month",
    deltaTone: "up",
  },
  {
    label: "Drafts open",
    value: "3",
    delta: "1 near ready",
    deltaTone: "flat",
  },
  {
    label: "Days itinerated",
    value: "36",
    delta: "+12 vs last month",
    deltaTone: "up",
  },
  {
    label: "Planned spend",
    value: "LKR 505k",
    delta: "8% under budget",
    deltaTone: "down",
  },
];

export const DRAFT_TRIPS = [
  {
    id: "draft-1",
    title: "Untitled trip",
    where: "Destination not set",
    edited: "2 hours ago",
    stage: "Collecting preferences",
    pct: 18,
    prompt:
      "“I want a 6-day trip under LKR 120,000. We prefer beaches and cultural sites rather than city crowds…”",
    days: 6,
  },
  {
    id: "draft-2",
    title: "Hill country loop",
    where: "Nuwara Eliya · Kandy · Ella",
    edited: "yesterday",
    stage: "Choosing hotels",
    pct: 62,
    prompt:
      "“Ten days across the hill country, mixing Nuwara Eliya and Kandy. Budget around LKR 250,000 for two people…”",
    days: 10,
  },
  {
    id: "draft-3",
    title: "Sri Lanka adventure",
    where: "Yala · Mirissa · Galle",
    edited: "3 days ago",
    stage: "Budget optimisation",
    pct: 84,
    prompt:
      "“Family trip with two kids, we want to see elephants and beaches. Eight days total, flexible on timing…”",
    days: 8,
  },
];

function buildGeneratedTrip({
  dayCount,
  travellers,
  budget,
  generated,
  plan,
  ...rest
}) {
  return {
    ...rest,
    dayCount,
    facts: [
      { label: "Length", value: `${dayCount} days` },
      { label: "Travellers", value: String(travellers) },
      { label: "Budget", value: budget },
      { label: "Generated", value: generated },
    ],
    days: plan.map(([label, stops]) => ({ label, stops })),
  };
}

export const GENERATED_TRIPS = [
  buildGeneratedTrip({
    id: "generated-1",
    title: "7 days in the Cultural Triangle",
    where: "Sigiriya · Polonnaruwa · Kandy",
    coverImageUrl: null,
    coverHint: "Sigiriya cover photo",
    dayCount: 7,
    travellers: 2,
    budget: "LKR 310,000",
    generated: "yesterday",
    plan: [
      ["Day 1", "Sigiriya Rock Fortress · Water gardens · Hotel Sigiriya"],
      ["Day 2", "Pidurangala sunrise · Minneriya safari · Village lunch"],
      ["Day 3", "Polonnaruwa ruins · Gal Vihara · Cycle the sacred quadrangle"],
    ],
  }),
  buildGeneratedTrip({
    id: "generated-2",
    title: "5 days on the south coast",
    where: "Galle · Mirissa · Tangalle",
    coverImageUrl: null,
    coverHint: "Galle Fort cover photo",
    dayCount: 5,
    travellers: 2,
    budget: "LKR 195,000",
    generated: "4 days ago",
    plan: [
      ["Day 1", "Galle Fort ramparts · Sea Spray dinner · Amangalla"],
      ["Day 2", "Mirissa whale watching · Coconut Tree Hill sunset"],
    ],
  }),
];
