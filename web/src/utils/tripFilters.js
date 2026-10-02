import { TRIP_STATUS } from "../constants/tripStatus";

// Segmented-control labels, in display order, and the status each one shows.
export const TRIP_FILTERS = ["All", "Drafts", "Generated", "Saved"];

const FILTER_STATUS = {
  All: null,
  Drafts: TRIP_STATUS.DRAFT,
  Generated: TRIP_STATUS.GENERATED,
  Saved: TRIP_STATUS.SAVED,
};

export function tripLength(trip) {
  return trip.dayCount ?? trip.days;
}

export const TRIP_SORTS = {
  Recent: null,
  Name: (a, b) => a.title.localeCompare(b.title),
  Longest: (a, b) => tripLength(b) - tripLength(a),
};

function matchesQuery(trip, query) {
  if (!query) return true;
  const haystack = [trip.title, trip.where, trip.prompt, trip.stage]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return haystack.includes(query);
}

// Splits trips into the three page sections for one filter and search query.
// `query` must already be trimmed and lower-case. A filter other than "All"
// leaves the other sections empty, and shownCount is the number of trips shown.
export function groupTrips(trips, { filter = "All", query = "", sort = null }) {
  const status = FILTER_STATUS[filter] ?? null;
  const pick = (wanted) => {
    if (status && status !== wanted) return [];
    const matching = trips.filter(
      (trip) => trip.status === wanted && matchesQuery(trip, query),
    );
    return sort ? [...matching].sort(sort) : matching;
  };
  const saved = pick(TRIP_STATUS.SAVED);
  const generated = pick(TRIP_STATUS.GENERATED);
  const drafts = pick(TRIP_STATUS.DRAFT);
  return {
    saved,
    generated,
    drafts,
    shownCount: saved.length + generated.length + drafts.length,
  };
}
