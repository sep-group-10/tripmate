import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import StatRow from "../components/StatRow";
import DraftTripCard from "../components/DraftTripCard";
import GeneratedTripCard from "../components/GeneratedTripCard";
import {
  discardDraftTrip,
  listTrips,
  renameDraftTrip,
  saveTrip,
  unsaveTrip,
} from "../services/tripsService";
import { parseApiError } from "../utils/apiError";
import { TRIP_FILTERS, TRIP_SORTS, groupTrips } from "../utils/tripFilters";

function MyTripsPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("Recent");
  const [filter, setFilter] = useState("All");
  const [trips, setTrips] = useState([]);
  const [loadStatus, setLoadStatus] = useState("loading");
  const [loadError, setLoadError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [pendingTripIds, setPendingTripIds] = useState({});

  useEffect(() => {
    let cancelled = false;
    listTrips()
      .then((loadedTrips) => {
        if (cancelled) return;
        setTrips(loadedTrips);
        setLoadStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        setLoadError(parseApiError(error).message);
        setLoadStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  const q = query.trim().toLowerCase();
  const sortFn = TRIP_SORTS[sort];

  const { saved, generated, drafts, shownCount } = useMemo(
    () => groupTrips(trips, { filter, query: q, sort: sortFn }),
    [trips, filter, q, sortFn],
  );
  const isEmpty = shownCount === 0;
  const draftCount = trips.filter((trip) => trip.status === "DRAFT").length;
  const itineratedDays = trips.reduce(
    (total, trip) =>
      trip.status === "DRAFT" ? total : total + (Number(trip.dayCount) || 0),
    0,
  );
  const plannedSpend = trips.reduce(
    (total, trip) => total + (Number(trip.budget) || 0),
    0,
  );
  const stats = [
    {
      label: "Trips planned",
      value: String(trips.length),
      delta: "In your account",
    },
    {
      label: "Drafts open",
      value: String(draftCount),
      delta: "Still in progress",
    },
    {
      label: "Days itinerated",
      value: String(itineratedDays),
      delta: "Generated and saved trips",
    },
    {
      label: "Planned spend",
      value: `LKR ${plannedSpend.toLocaleString("en-US", { maximumFractionDigits: 0 })}`,
      delta: "Sum of trip budgets",
    },
  ];

  const clearFilters = () => {
    setQuery("");
    setFilter("All");
  };

  const changeTripStatus = async (action, trip) => {
    setPendingTripIds((current) => ({ ...current, [trip.id]: true }));
    try {
      const updatedTrip = await action(trip.id);
      setTrips((current) =>
        current.map((item) =>
          item.id === updatedTrip.id ? updatedTrip : item,
        ),
      );
    } catch (error) {
      toast.error(parseApiError(error).message);
    } finally {
      setPendingTripIds((current) => {
        const next = { ...current };
        delete next[trip.id];
        return next;
      });
    }
  };

  const renameDraft = async (trip, title) => {
    setPendingTripIds((current) => ({ ...current, [trip.id]: true }));
    try {
      const updatedTrip = await renameDraftTrip(trip.id, title);
      setTrips((current) =>
        current.map((item) =>
          item.id === updatedTrip.id ? updatedTrip : item,
        ),
      );
      toast.success("Draft renamed");
      return true;
    } catch (error) {
      toast.error(parseApiError(error).message);
      return false;
    } finally {
      setPendingTripIds((current) => {
        const next = { ...current };
        delete next[trip.id];
        return next;
      });
    }
  };

  const discardDraft = async (trip) => {
    setPendingTripIds((current) => ({ ...current, [trip.id]: true }));
    try {
      await discardDraftTrip(trip.id);
      setTrips((current) => current.filter((item) => item.id !== trip.id));
      toast.success("Draft discarded");
      return true;
    } catch (error) {
      toast.error(parseApiError(error).message);
      return false;
    } finally {
      setPendingTripIds((current) => {
        const next = { ...current };
        delete next[trip.id];
        return next;
      });
    }
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

        {loadStatus === "ready" && <StatRow stats={stats} />}

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
            {TRIP_FILTERS.map((label) => (
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

        {loadStatus === "loading" && (
          <p className="m-0 text-body-sm text-muted-600" role="status">
            Loading your trips…
          </p>
        )}

        {loadStatus === "error" && (
          <section
            className="flex flex-col items-center gap-3 rounded-card bg-surface px-8 py-14 text-center shadow-control"
            role="alert"
          >
            <h2 className="font-heading text-lg font-semibold tracking-tight text-ink">
              Trips could not be loaded
            </h2>
            <p className="max-w-85 text-body-sm text-muted-600">{loadError}</p>
            <button
              type="button"
              onClick={() => {
                setLoadError("");
                setReloadKey((key) => key + 1);
              }}
              className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
            >
              Try again
            </button>
          </section>
        )}

        {loadStatus === "ready" && saved.length > 0 && (
          <section className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2.5">
                <h2 className="font-heading text-lg font-semibold tracking-tight text-ink">
                  Saved trips
                </h2>
                <span className="rounded-pill border border-border bg-surface px-2.5 py-0.5 text-caption font-medium tabular-nums text-muted-700">
                  {saved.length}
                </span>
              </div>
              <p className="text-body-sm text-muted-600">
                Itineraries you've kept. Ready to view, share or export.
              </p>
            </div>
            <div className="flex flex-col gap-4">
              {saved.map((trip) => (
                <GeneratedTripCard
                  key={trip.id}
                  trip={trip}
                  actionPending={Boolean(pendingTripIds[trip.id])}
                  onUnsave={(item) => changeTripStatus(unsaveTrip, item)}
                  onViewItinerary={(item) =>
                    navigate(`/trips/${encodeURIComponent(item.id)}`)
                  }
                />
              ))}
            </div>
          </section>
        )}

        {loadStatus === "ready" && generated.length > 0 && (
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
                Trips with generated itineraries.
              </p>
            </div>
            <div className="flex flex-col gap-4">
              {generated.map((trip) => (
                <GeneratedTripCard
                  key={trip.id}
                  trip={trip}
                  actionPending={Boolean(pendingTripIds[trip.id])}
                  onSave={(item) => changeTripStatus(saveTrip, item)}
                  onKeepRefining={(item) =>
                    navigate(`/chat?tripId=${encodeURIComponent(item.id)}`)
                  }
                  onViewItinerary={(item) =>
                    navigate(`/trips/${encodeURIComponent(item.id)}`)
                  }
                />
              ))}
            </div>
          </section>
        )}

        {loadStatus === "ready" && drafts.length > 0 && (
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
                <DraftTripCard
                  key={trip.id}
                  trip={trip}
                  actionPending={Boolean(pendingTripIds[trip.id])}
                  onRename={renameDraft}
                  onDiscard={discardDraft}
                  onContinue={(item) =>
                    navigate(`/chat?tripId=${encodeURIComponent(item.id)}`)
                  }
                />
              ))}
            </div>
          </section>
        )}

        {loadStatus === "ready" && isEmpty && (
          <section className="flex flex-col items-center gap-3 rounded-card bg-surface px-8 py-14 text-center shadow-control">
            <h2 className="font-heading text-lg font-semibold tracking-tight text-ink">
              {trips.length === 0 ? "No trips yet" : "No trips match that"}
            </h2>
            <p className="max-w-85 text-body-sm text-muted-600">
              {trips.length === 0
                ? "Trips you create will appear here. Start planning your first trip."
                : "Try a different search term, or clear the filter to see every trip in your account."}
            </p>
            {trips.length > 0 && (
              <button
                type="button"
                onClick={clearFilters}
                className="mt-1 rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
              >
                Clear filters
              </button>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default MyTripsPage;
