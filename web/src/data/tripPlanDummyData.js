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
