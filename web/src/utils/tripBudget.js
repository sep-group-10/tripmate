import {
  HOTEL_BY_DESTINATION,
  HOTELS,
  ITINERARY_DAYS,
} from "../data/tripPlanDummyData";

// Same rate as _MISC_RATE in cost_estimator.py.
const MISC_RATE = 0.1;

// Category keys mirror cost_estimator.py's output. Each maps from an itinerary
// item category (legs map to local or intercity transport), so the breakdown is
// derived from ITINERARY_DAYS and always adds up to the Itinerary tab's total.
export const BUDGET_CATEGORIES = [
  { key: "accommodation", label: "Accommodation", color: "bg-accent" },
  { key: "dining", label: "Dining", color: "bg-info" },
  {
    key: "transport_intercity",
    label: "Intercity transport",
    color: "bg-success",
  },
  { key: "transport_local", label: "Local transport", color: "bg-warn" },
  { key: "activities", label: "Activities", color: "bg-accent-300" },
  { key: "miscellaneous", label: "Miscellaneous", color: "bg-muted-400" },
];

const ITEM_BUDGET_KEYS = {
  hotel: "accommodation",
  restaurant: "dining",
  attraction: "activities",
};

export function dayHotel(day) {
  return day.hotel_id ? HOTELS[day.hotel_id] : null;
}

// One night per day that has a hotel_id, priced per night, like
// _accommodation_cost in cost_estimator.py.
export function daySpend(day) {
  const hotel = dayHotel(day);
  return (
    [...day.items, ...day.legs].reduce((sum, row) => sum + row.cost, 0) +
    (hotel ? hotel.price_per_night : 0)
  );
}

// Shared by the Itinerary and Budget tabs so their totals always agree.
// Miscellaneous is MISC_RATE of the other categories' subtotal, as in
// cost_estimator.py. The real values exist there but aren't exposed on
// ChatResponse yet (and there they are min/max ranges, not single numbers).
export function computeBudget() {
  const amounts = Object.fromEntries(
    BUDGET_CATEGORIES.map(({ key }) => [key, 0]),
  );
  ITINERARY_DAYS.forEach((day) => {
    day.items.forEach((item) => {
      amounts[ITEM_BUDGET_KEYS[item.category]] += item.cost;
    });
    day.legs.forEach((leg) => {
      amounts[leg.intercity ? "transport_intercity" : "transport_local"] +=
        leg.cost;
    });
  });
  // Nights per hotel = days sharing its hotel_id, like _nights_per_destination.
  amounts.accommodation = Object.values(HOTEL_BY_DESTINATION).reduce(
    (sum, hotelId) =>
      sum +
      HOTELS[hotelId].price_per_night *
        ITINERARY_DAYS.filter((day) => day.hotel_id === hotelId).length,
    0,
  );
  const subtotal = Object.values(amounts).reduce((sum, n) => sum + n, 0);
  amounts.miscellaneous = Math.round(subtotal * MISC_RATE);
  return { amounts, total: subtotal + amounts.miscellaneous };
}
