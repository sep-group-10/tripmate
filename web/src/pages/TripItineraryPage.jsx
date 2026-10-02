import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getTripDetails } from "../services/tripsService";
import { parseApiError } from "../utils/apiError";
import { formatDateRange, formatMoney } from "../utils/tripFormat";

function TripItineraryPage() {
  const { tripId } = useParams();
  const [status, setStatus] = useState("loading");
  const [trip, setTrip] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getTripDetails(tripId)
      .then((details) => {
        if (cancelled) return;
        setTrip(details);
        setStatus("ready");
      })
      .catch((requestError) => {
        if (cancelled) return;
        setError(parseApiError(requestError).message);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [tripId]);

  const dateRange = trip
    ? formatDateRange(trip.travel_start_date, trip.travel_end_date, {
        withYear: true,
      })
    : "";

  return (
    <div className="font-body bg-bg text-ink">
      <main className="mx-auto flex max-w-245 flex-col gap-6 px-6 py-14">
        <Link
          to="/trips"
          className="w-fit text-body-sm font-medium text-accent-700 hover:underline"
        >
          ← Back to My trips
        </Link>
        {status === "loading" && (
          <p role="status" className="text-body-sm text-muted-600">
            Loading itinerary…
          </p>
        )}
        {status === "error" && (
          <section
            role="alert"
            className="rounded-card bg-surface p-8 shadow-control"
          >
            <h1 className="font-heading text-heading-md font-semibold">
              Itinerary could not be loaded
            </h1>
            <p className="text-body-sm text-muted-600">{error}</p>
          </section>
        )}
        {status === "ready" && trip && (
          <>
            <header className="rounded-card bg-surface p-7 shadow-control">
              <span className="font-mono text-eyebrow tracking-widest text-muted-600 uppercase">
                {trip.destination || "Trip destination"}
              </span>
              <h1 className="mt-2 font-heading text-heading-md font-semibold tracking-tight">
                {trip.title || trip.destination || "Trip itinerary"}
              </h1>
              <div className="mt-4 flex flex-wrap gap-x-7 gap-y-2 text-body-sm text-muted-700">
                {dateRange && <span>{dateRange}</span>}
                {trip.duration != null && <span>{trip.duration} days</span>}
                {trip.budget != null && (
                  <span>Budget: {formatMoney(Number(trip.budget))}</span>
                )}
              </div>
            </header>
            {trip.itinerary?.days?.length ? (
              <div className="flex flex-col gap-4">
                {trip.itinerary.days.map((day) => (
                  <section
                    key={day.id}
                    className="rounded-card bg-surface p-6 shadow-control"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-divider pb-3">
                      <div>
                        <h2 className="font-heading text-lg font-semibold">
                          Day {day.day_number}
                          {day.title ? ` · ${day.title}` : ""}
                        </h2>
                        <p className="m-0 text-body-sm text-muted-600">
                          {day.date}
                        </p>
                      </div>
                    </div>
                    {day.summary && (
                      <p className="text-body-sm text-muted-700">
                        {day.summary}
                      </p>
                    )}
                    {day.items.length ? (
                      <ol className="mt-3 flex flex-col divide-y divide-divider">
                        {day.items.map((item) => (
                          <li
                            key={item.id}
                            className="flex flex-col gap-1 py-3 first:pt-0 last:pb-0 sm:flex-row sm:gap-5"
                          >
                            <span className="w-30 flex-none text-body-sm font-medium text-accent-700">
                              {[item.start_time, item.end_time]
                                .filter(Boolean)
                                .map((value) => value.slice(0, 5))
                                .join(" – ") || item.item_type}
                            </span>
                            <div>
                              <h3 className="m-0 text-body-sm font-semibold">
                                {item.title}
                              </h3>
                              {item.description && (
                                <p className="m-0 mt-1 text-body-sm text-muted-600">
                                  {item.description}
                                </p>
                              )}
                              {item.location && (
                                <p className="m-0 mt-1 text-caption text-muted-600">
                                  {item.location}
                                </p>
                              )}
                            </div>
                          </li>
                        ))}
                      </ol>
                    ) : (
                      <p className="text-body-sm text-muted-600">
                        No activities are recorded for this day.
                      </p>
                    )}
                  </section>
                ))}
              </div>
            ) : (
              <section className="rounded-card bg-surface px-8 py-12 text-center shadow-control">
                <h2 className="font-heading text-lg font-semibold">
                  No itinerary available
                </h2>
                <p className="text-body-sm text-muted-600">
                  This trip does not have a persisted itinerary yet.
                </p>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default TripItineraryPage;
