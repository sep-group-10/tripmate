// PLACEHOLDER DATA for the trip-plan page. Nothing here comes from the backend:
// it is a hardcoded Kandy and Ella sample, shaped like the real
// ChatResponse / ChatItineraryDay (backend/app/schemas/chat.py) so the page can
// be wired to /api/v1/chat later by replacing these imports.

// Dummy itinerary, shaped like ChatItineraryDay / ChatItineraryItem
// (backend/app/schemas/chat.py): day_number, date, items[] with candidate_id,
// category, name, start_time, end_time, and route_optimization.local_distance_km.
// The real schema has NO costs, travel legs or day titles yet, so `cost` (LKR,
// for both travellers), `legs` (one per gap between items; `intercity` marks the
// long drive) and `title` below are dummy-only extras that the backend would need
// to add before this can be wired to a ChatResponse. Place names come from the
// seeded Kandy data; Ella has no seeded places yet.
export const ITINERARY_DAYS = [
  {
    day_number: 1,
    date: "2026-10-12",
    title: "Kandy heritage & lake",
    route_optimization: { local_distance_km: 4.1 },
    hotel_id: "hotel-kandy",
    items: [
      {
        candidate_id: "attr-1",
        category: "attraction",
        name: "Temple of the Sacred Tooth Relic",
        start_time: "09:00",
        end_time: "11:00",
        cost: 4000,
      },
      {
        candidate_id: "rest-1",
        category: "restaurant",
        name: "Lunch at Kandy Spice Garden",
        start_time: "12:00",
        end_time: "13:15",
        cost: 3600,
      },
      {
        candidate_id: "attr-2",
        category: "attraction",
        name: "Kandy Lake",
        start_time: "14:00",
        end_time: "15:30",
        cost: 0,
      },
    ],
    legs: [
      { mode: "Tuk-tuk", duration_minutes: 10, cost: 600 },
      { mode: "Tuk-tuk", duration_minutes: 8, cost: 500 },
    ],
  },
  {
    day_number: 2,
    date: "2026-10-13",
    title: "Kandy to Ella",
    route_optimization: { local_distance_km: 9.4 },
    hotel_id: "hotel-ella",
    items: [
      {
        candidate_id: "attr-3",
        category: "attraction",
        name: "Royal Botanical Gardens",
        start_time: "08:00",
        end_time: "10:00",
        cost: 6000,
      },
      {
        candidate_id: "attr-4",
        category: "attraction",
        name: "Nine Arch Bridge",
        start_time: "15:00",
        end_time: "16:00",
        cost: 0,
      },
      {
        candidate_id: "rest-2",
        category: "restaurant",
        name: "Dinner in Ella town",
        start_time: "19:00",
        end_time: "20:30",
        cost: 5000,
      },
    ],
    legs: [
      { mode: "Car", duration_minutes: 255, cost: 24000, intercity: true },
      { mode: "Tuk-tuk", duration_minutes: 12, cost: 1200 },
    ],
  },
  {
    day_number: 3,
    date: "2026-10-14",
    title: "Ella viewpoints",
    route_optimization: { local_distance_km: 14.8 },
    hotel_id: null, // departure day: no overnight stay
    items: [
      {
        candidate_id: "attr-5",
        category: "attraction",
        name: "Ella Rock",
        start_time: "06:30",
        end_time: "10:30",
        cost: 3000,
      },
      {
        candidate_id: "rest-3",
        category: "restaurant",
        name: "Lunch in Ella town",
        start_time: "12:00",
        end_time: "13:15",
        cost: 4500,
      },
      {
        candidate_id: "attr-6",
        category: "attraction",
        name: "Little Adam's Peak",
        start_time: "15:30",
        end_time: "17:30",
        cost: 0,
      },
    ],
    legs: [
      { mode: "Tuk-tuk", duration_minutes: 15, cost: 1200 },
      { mode: "Tuk-tuk", duration_minutes: 10, cost: 800 },
    ],
  },
];

// Hotel data as cost_estimator.py sees it: each day carries the hotel_id of the
// night it ends with, the itinerary maps destination -> hotel_id
// (hotel_by_destination), and the nightly price lives on the hotel candidate,
// which is stood in for by HOTELS here. ChatItineraryDay's hotel_location is
// left out because nothing on this page draws it yet. 3 days = 2 nights.
export const HOTEL_BY_DESTINATION = {
  Kandy: "hotel-kandy",
  Ella: "hotel-ella",
};

export const HOTELS = {
  "hotel-kandy": { name: "Hill View Kandy", price_per_night: 14000 },
  "hotel-ella": { name: "Ella guesthouse", price_per_night: 12000 },
};

export const TRIP_FACTS = {
  title: "Three days from Kandy to Ella",
  places: "Kandy · Ella",
  travellers: "2 adults",
  pace: "Relaxed",
};

export const TRADEOFFS = [
  {
    tag: "Swapped",
    tone: "info",
    text: "The Royal Botanical Gardens moved to Day 2 morning — it sits on the road out of Kandy, so it fills the time before the long drive to Ella without backtracking.",
  },
  {
    tag: "Kept",
    tone: "success",
    text: "The private car for Kandy to Ella stayed despite the cost: the drive is about four hours, while the scenic train is closer to seven.",
  },
  {
    tag: "Dropped",
    tone: "warn",
    text: "Sigiriya — it's a long detour from Kandy and doesn't fit a relaxed pace with two travellers on a three-day trip.",
  },
];

// Dummy route legs, consistent with the day data above (Kandy to Ella is about
// 137 km and roughly four hours by road).
export const ROUTE_LEGS = [
  {
    label: "Leg 1",
    text: "Day 1 → Day 2 · Kandy Lake → Royal Botanical Gardens, by tuk-tuk",
    distance_km: 6.2,
    duration_minutes: 20,
  },
  {
    label: "Leg 2",
    text: "Day 2 · Royal Botanical Gardens → Nine Arch Bridge, Kandy to Ella by car",
    distance_km: 137,
    duration_minutes: 255,
  },
  {
    label: "Leg 3",
    text: "Day 2 → Day 3 · Nine Arch Bridge → Ella Rock trailhead, by tuk-tuk",
    distance_km: 4.8,
    duration_minutes: 15,
  },
];

// Dummy content is shaped loosely like ChatItineraryDay / ChatItineraryItem
// (backend/app/schemas/chat.py) so it can be swapped for a real ChatResponse.
// `stops` are place names (in a real response, itinerary items[].name) and
// `actions` are short follow-up prompts shown under an assistant message.
export const INITIAL_MESSAGES = [
  {
    id: "m1",
    role: "assistant",
    text: "Hi! Tell me where you'd like to go, for how long and what you enjoy, and I'll sketch a plan. Here's a sample of what a day can look like:",
    stops: ["Sacred Tooth Relic", "Kandy Spice Garden", "Kandy Lake"],
    actions: ["Make it cheaper", "Add a rest day", "Regenerate Day 1"],
    itineraryDay: ITINERARY_DAYS[0],
  },
  {
    id: "m2",
    role: "user",
    text: "Plan 3 days in Kandy and Ella for two, we love food and walking.",
  },
];

export const DUMMY_REPLIES = [
  "Got it - I'll keep that in mind and rework the plan around it. (Placeholder reply, no AI is connected yet.)",
  "Sure, I can adjust that. (Placeholder reply, no AI is connected yet.)",
  "Noted! Anything else you'd like to change? (Placeholder reply, no AI is connected yet.)",
];
