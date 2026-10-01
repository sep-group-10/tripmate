import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import StatRow from "../components/StatRow";
import DraftTripCard from "../components/DraftTripCard";
import GeneratedTripCard from "../components/GeneratedTripCard";
import { STATS, DRAFT_TRIPS, GENERATED_TRIPS } from "../data/myTripsDummyData";

function tripLength(trip) {
  return trip.dayCount ?? trip.days;
}

const SORTS = {
  Recent: null,
  Name: (a, b) => a.title.localeCompare(b.title),
  Longest: (a, b) => tripLength(b) - tripLength(a),
};

const FILTERS = ["All", "Drafts", "Generated"];

function matchesQuery(trip, query, extraFields = []) {
  if (!query) return true;
  const haystack = [trip.title, trip.where, ...extraFields]
    .join(" ")
    .toLowerCase();
  return haystack.includes(query);
}

function MyTripsPage() {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("Recent");
  const [filter, setFilter] = useState("All");

  const q = query.trim().toLowerCase();
  const sortFn = SORTS[sort];

  const drafts = useMemo(() => {
    const filtered = DRAFT_TRIPS.filter((trip) =>
      matchesQuery(trip, q, [trip.prompt, trip.stage]),
    );
    return sortFn ? [...filtered].sort(sortFn) : filtered;
  }, [q, sortFn]);

  const generated = useMemo(() => {
    const filtered = GENERATED_TRIPS.filter((trip) => matchesQuery(trip, q));
    return sortFn ? [...filtered].sort(sortFn) : filtered;
  }, [q, sortFn]);

  const showDrafts = filter !== "Generated" && drafts.length > 0;
  const showGenerated = filter !== "Drafts" && generated.length > 0;
  const shownCount =
    (filter !== "Generated" ? drafts.length : 0) +
    (filter !== "Drafts" ? generated.length : 0);
  const isEmpty = shownCount === 0;

  const clearFilters = () => {
    setQuery("");
    setFilter("All");
  };

  return (
    <div className="font-body bg-bg text-ink">
      <main className="mx-auto flex max-w-245 flex-col gap-7 px-6 py-14">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
              TripMate · Planner
            </span>
            <h1 className="mt-2 font-heading text-heading-md font-semibold tracking-tight text-ink">
              My trips
            </h1>
            <p className="mt-1.5 max-w-115 text-body-sm text-muted-600">
              Pick up a planning session where you left it, or revisit an
              itinerary TripMate has already generated.
            </p>
          </div>
          <Link
            to="/chat"
            className="rounded-pill bg-accent px-4 py-2.5 text-body-sm font-medium text-white shadow-control hover:bg-accent-600"
          >
            New trip
          </Link>
        </div>

        <StatRow stats={STATS} />

        <div className="flex flex-wrap items-center gap-3">
          <input
            type="text"
            placeholder="Search trips…"
            aria-label="Search trips"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-65 rounded-pill border border-border bg-surface px-3.5 py-2.5 text-body-sm shadow-control outline-none placeholder:text-muted-500 focus:border-accent"
          />
          <select
            aria-label="Sort trips"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="rounded-pill border border-border bg-surface px-3.5 py-2.5 text-body-sm shadow-control outline-none focus:border-accent"
          >
            <option value="Recent">Recently edited</option>
            <option value="Name">Trip name</option>
            <option value="Longest">Longest trip</option>
          </select>
          <span className="inline-flex gap-0.5 rounded-pill bg-muted-300 p-0.75">
            {FILTERS.map((label) => (
              <button
                key={label}
                type="button"
                onClick={() => setFilter(label)}
                className={`rounded-pill px-3.5 py-1.5 text-label font-medium ${
                  filter === label
                    ? "bg-surface text-ink shadow-control"
                    : "text-muted-700"
                }`}
              >
                {label}
              </button>
            ))}
          </span>
          <span className="ml-auto font-mono text-badge font-medium tracking-wider text-muted-600 uppercase">
            {shownCount} {shownCount === 1 ? "trip" : "trips"}
          </span>
        </div>

        {showDrafts && (
          <section className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2.5">
                <h2 className="font-heading text-lg font-semibold tracking-tight text-ink">
                  Drafts
                </h2>
                <span className="rounded-pill border border-border bg-surface px-2.5 py-0.5 text-caption font-medium tabular-nums text-muted-700">
                  {drafts.length}
                </span>
              </div>
              <p className="text-body-sm text-muted-600">
                Planning sessions that haven't produced a final itinerary yet.
              </p>
            </div>
            <div className="flex flex-col gap-4">
              {drafts.map((trip) => (
                <DraftTripCard key={trip.id} trip={trip} />
              ))}
            </div>
          </section>
        )}

        {showGenerated && (
          <section className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2.5">
                <h2 className="font-heading text-lg font-semibold tracking-tight text-ink">
                  Generated itineraries
                </h2>
                <span className="rounded-pill border border-border bg-surface px-2.5 py-0.5 text-caption font-medium tabular-nums text-muted-700">
                  {generated.length}
                </span>
              </div>
              <p className="text-body-sm text-muted-600">
                Complete day-by-day plans — ready to review, refine or book.
              </p>
            </div>
            <div className="flex flex-col gap-4">
              {generated.map((trip) => (
                <GeneratedTripCard key={trip.id} trip={trip} />
              ))}
            </div>
          </section>
        )}

        {isEmpty && (
          <section className="flex flex-col items-center gap-3 rounded-card bg-surface px-8 py-14 text-center shadow-control">
            <h2 className="font-heading text-lg font-semibold tracking-tight text-ink">
              No trips match that
            </h2>
            <p className="max-w-85 text-body-sm text-muted-600">
              Try a different search term, or clear the filter to see every trip
              in your account.
            </p>
            <button
              type="button"
              onClick={clearFilters}
              className="mt-1 rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
            >
              Clear filters
            </button>
          </section>
        )}
      </main>
    </div>
  );
}

export default MyTripsPage;
