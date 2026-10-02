// PLACEHOLDER DATA for the trip-plan page's Summary and Budget tabs. Nothing
// here comes from the backend: there is no trips/itinerary endpoint with hero
// facts, trade-offs or costs yet (the /chat response carries only the schedule,
// which the Itinerary and Map tabs already render). Shaped in snake_case per
// docs/api-contract.md so a real response can replace this object as-is.
export const TRIP_DUMMY = {
  summary: {
    route_label: "Kandy · Nuwara Eliya · Ella",
    title: "Seven days through the hill country",
    occasion: "5th anniversary",
    start_date: "2026-09-12",
    end_date: "2026-09-18",
    stop_count: 12,
    travellers: 2,
    pace: "Relaxed",
    optimised_for:
      "Your itinerary balances the landmarks with quieter neighbourhood hours — the Nine Arch Bridge at dawn before the crowds, and Sigiriya on Day 5 so the climb lands on the coolest morning of the week. Accommodation is anchored at 98 Acres so walks stay short on Days 2 and 3, and spend peaks on Day 1 with the Kandy House dinner.",
    tradeoffs: [
      {
        type: "swapped",
        text: "Horton Plains moved to Day 6 — the Day 4 forecast showed cloud cover before 09:00, which would have hidden World's End.",
      },
      {
        type: "kept",
        text: "The Kandy House stayed despite the price: it's the only stay within walking distance of the Temple ceremony.",
      },
      {
        type: "dropped",
        text: "Adam's Peak — the climb needs a 02:00 start and doesn't fit a relaxed pace with two travellers.",
      },
    ],
  },
  budget: {
    total: 310400,
    per_day: 44340,
    currency: "LKR",
    categories: [
      { key: "accommodation", label: "Accommodation", amount: 148000 },
      { key: "dining", label: "Dining", amount: 74400 },
      { key: "transport", label: "Transport & driver", amount: 46600 },
      { key: "attractions", label: "Attractions", amount: 27900 },
      { key: "misc", label: "Market & misc", amount: 13500 },
    ],
  },
};

// Dev-only sample plan for the Map and Itinerary tabs, shaped like the real
// ChatItinerary (backend/app/schemas/chat.py) and consistent with the summary
// above (7 days, 12 stops). Only the ?demo=1 and "Load sample trip" dev paths
// use it, so it is dropped from production builds.
const stop = (id, category, name, start, end, latitude, longitude) => ({
  candidate_id: id,
  category,
  name,
  start_time: start,
  end_time: end,
  latitude,
  longitude,
});

export const DEMO_ITINERARY = {
  status: "completed",
  days: [
    {
      day_number: 1,
      date: "2026-09-12",
      day_type: "arrival",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 3.2 },
      items: [
        stop(
          "a1",
          "attraction",
          "Temple of the Sacred Tooth Relic",
          "17:30",
          "19:00",
          7.2936,
          80.6413,
        ),
        stop(
          "r1",
          "restaurant",
          "Dinner at The Kandy House",
          "20:00",
          "22:00",
          7.2906,
          80.6337,
        ),
      ],
    },
    {
      day_number: 2,
      date: "2026-09-13",
      day_type: "full",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 5.8 },
      items: [
        stop(
          "a2",
          "attraction",
          "Royal Botanical Gardens, Peradeniya",
          "09:00",
          "12:00",
          7.2697,
          80.5966,
        ),
        stop(
          "r2",
          "restaurant",
          "Lunch at The Empire Cafe",
          "13:00",
          "15:30",
          7.2928,
          80.6415,
        ),
      ],
    },
    {
      day_number: 3,
      date: "2026-09-14",
      day_type: "full",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 7.4 },
      items: [
        stop(
          "a3",
          "attraction",
          "Nine Arch Bridge at dawn",
          "06:15",
          "07:30",
          6.8768,
          81.0608,
        ),
        stop(
          "a4",
          "attraction",
          "Pedro Tea Estate tasting",
          "16:00",
          "17:30",
          6.9765,
          80.7545,
        ),
      ],
    },
    {
      day_number: 4,
      date: "2026-09-15",
      day_type: "full",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 4.1 },
      items: [
        stop(
          "a5",
          "attraction",
          "Little Adam's Peak",
          "08:00",
          "11:00",
          6.8667,
          81.0466,
        ),
        stop(
          "r3",
          "restaurant",
          "Tea-estate lunch above Ella",
          "13:00",
          "14:30",
          6.879,
          81.05,
        ),
      ],
    },
    {
      day_number: 5,
      date: "2026-09-16",
      day_type: "full",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 9.6 },
      items: [
        stop(
          "a6",
          "attraction",
          "Sigiriya Rock Fortress",
          "06:00",
          "09:30",
          7.957,
          80.7603,
        ),
        stop(
          "a7",
          "attraction",
          "Minneriya elephant safari",
          "15:00",
          "18:00",
          8.0357,
          80.8993,
        ),
      ],
    },
    {
      day_number: 6,
      date: "2026-09-17",
      day_type: "full",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 2.0 },
      items: [
        stop(
          "a8",
          "attraction",
          "World's End and Baker's Falls",
          "05:30",
          "10:00",
          6.8014,
          80.8008,
        ),
      ],
    },
    {
      day_number: 7,
      date: "2026-09-18",
      day_type: "departure",
      hotel_id: null,
      warnings: [],
      route_optimization: { local_distance_km: 1.2 },
      items: [
        stop(
          "a9",
          "attraction",
          "Kandy market, gifts",
          "10:00",
          "12:00",
          7.2927,
          80.635,
        ),
      ],
    },
  ],
  hotel_by_destination: {},
  unscheduled: [],
  warnings: [],
};
