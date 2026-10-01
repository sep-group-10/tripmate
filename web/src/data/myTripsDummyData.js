// PLACEHOLDER DATA for the My Trips page. Nothing here comes from the
// backend: there is no GET /trips endpoint yet, Trip has no title field,
// and the chat flow never persists Itinerary/ItineraryDay rows (see
// backend/app/routers/chat.py - the day-by-day plan is returned in the
// API response only and thrown away). Replace these imports once that
// backend work lands. services/tripsService.js seeds its in-memory store from
// MY_TRIPS, which holds every trip with a `status` (DRAFT, GENERATED, SAVED).

import { TRIP_STATUS } from "../constants/tripStatus";

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

const DRAFT_TRIPS = [
  {
    id: "draft-1",
    status: TRIP_STATUS.DRAFT,
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
    status: TRIP_STATUS.DRAFT,
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
    status: TRIP_STATUS.DRAFT,
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

const GENERATED_AND_SAVED_TRIPS = [
  buildGeneratedTrip({
    id: "generated-1",
    status: TRIP_STATUS.GENERATED,
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
    status: TRIP_STATUS.GENERATED,
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
  buildGeneratedTrip({
    id: "saved-1",
    status: TRIP_STATUS.SAVED,
    title: "4 days in Kandy and Ella",
    where: "Kandy · Nuwara Eliya · Ella",
    coverImageUrl: null,
    coverHint: "Nine Arch Bridge cover photo",
    dayCount: 4,
    travellers: 2,
    budget: "LKR 240,000",
    generated: "last week",
    plan: [
      ["Day 1", "Temple of the Sacred Tooth Relic · Kandy Lake · Dinner"],
      ["Day 2", "Royal Botanical Gardens · Scenic drive to Nuwara Eliya"],
      ["Day 3", "Nine Arch Bridge at dawn · Little Adam's Peak"],
    ],
  }),
  buildGeneratedTrip({
    id: "saved-2",
    status: TRIP_STATUS.SAVED,
    title: "6 days of beaches and culture",
    where: "Negombo · Galle · Unawatuna",
    coverImageUrl: null,
    coverHint: "Unawatuna cover photo",
    dayCount: 6,
    travellers: 4,
    budget: "LKR 380,000",
    generated: "2 weeks ago",
    plan: [
      ["Day 1", "Negombo fish market · Lagoon sunset"],
      ["Day 2", "Galle Fort walk · Dutch Reformed Church"],
    ],
  }),
];

// Every trip with its `status`, in no particular order: the page groups them.
export const MY_TRIPS = [...GENERATED_AND_SAVED_TRIPS, ...DRAFT_TRIPS];
