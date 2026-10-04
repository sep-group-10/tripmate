import { useEffect, useState } from "react";
import { TRIP_STATUS } from "../constants/tripStatus";
import { PILL_TONES } from "../utils/pillTones";
import { formatMoney } from "../utils/tripFormat";
import { getTripDetails } from "../services/tripsService";

// GENERATED is informational (blue) so it stays distinct from the green SAVED.
const STATUS_PILLS = {
  [TRIP_STATUS.GENERATED]: { label: "Generated", tone: PILL_TONES.info },
  [TRIP_STATUS.SAVED]: { label: "Saved", tone: PILL_TONES.success },
};

/** Card for a completed itinerary (GENERATED or SAVED): cover photo with
 * overlaid title, a quick-facts strip, a day-by-day summary and actions.
 * A generated trip can be saved (`onSave`); a saved trip can be removed from
 * saved (`onUnsave`). */
function GeneratedTripCard({
  trip,
  onSave,
  onUnsave,
  onKeepRefining,
  onViewItinerary,
  actionPending = false,
}) {
  const isSaved = trip.status === TRIP_STATUS.SAVED;
  const pill = STATUS_PILLS[trip.status] ?? STATUS_PILLS[TRIP_STATUS.GENERATED];
  const [details, setDetails] = useState(null);
  const [previewStatus, setPreviewStatus] = useState("loading");

  useEffect(() => {
    let cancelled = false;
    getTripDetails(trip.id)
      .then((tripDetails) => {
        if (cancelled) return;
        setDetails(tripDetails);
        setPreviewStatus(
          tripDetails.itinerary?.days?.length ? "ready" : "empty",
        );
      })
      .catch(() => {
        if (!cancelled) setPreviewStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [trip.id]);

  const itineraryDays = (details?.itinerary?.days ?? []).map((day) => ({
    id: day.id,
    label: `Day ${day.day_number}`,
    stops:
      day.items
        ?.map((item) => item.title)
        .filter(Boolean)
        .join(" · ") ||
      day.summary ||
      "No activities recorded",
  }));
  const facts = [
    {
      label: "Length",
      value: `${trip.dayCount || itineraryDays.length || 0} days`,
    },
    {
      label: "Travellers",
      value: trip.travelers ?? trip.travellers ?? "Not specified",
    },
    {
      label: "Budget",
      value: trip.budget > 0 ? formatMoney(trip.budget) : "Not specified",
    },
    { label: isSaved ? "Updated" : "Generated", value: trip.edited || "—" },
  ];
  const destination = details?.destination || trip.where;

  return (
    <article className="flex flex-col overflow-hidden rounded-card bg-surface shadow-control">
      <div className="relative h-50">
        {trip.coverImageUrl ? (
          <img
            src={trip.coverImageUrl}
            alt=""
            className="h-full w-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-[repeating-linear-gradient(135deg,var(--color-bg)_0_7px,rgba(23,25,26,0.05)_7px_8px)] font-mono text-caption tracking-wider text-muted-500 uppercase">
            {destination || "Trip itinerary"}
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 via-45% to-transparent to-70%" />
        <span
          className={`absolute top-4 left-4 rounded-pill px-2.5 py-1 text-caption font-medium ${pill.tone}`}
        >
          {pill.label}
        </span>
        <div className="absolute bottom-4 left-5 flex flex-col gap-0.5">
          <span className="font-mono text-caption tracking-widest text-white/80 uppercase">
            {destination}
          </span>
          <h3 className="font-heading text-xl font-semibold tracking-tight text-white">
            {trip.title}
          </h3>
        </div>
      </div>

      <div className="flex flex-col gap-4 p-5.5">
        <div className="grid grid-cols-2 gap-3.5 rounded-lg bg-bg p-4 sm:grid-cols-4">
          {facts.map((fact) => (
            <div key={fact.label} className="flex flex-col gap-0.5">
              <span className="text-eyebrow font-medium text-muted-600">
                {fact.label}
              </span>
              <span className="text-body-sm font-medium text-ink">
                {fact.value}
              </span>
            </div>
          ))}
        </div>

        <div className="flex flex-col">
          {previewStatus === "loading" && (
            <p
              role="status"
              className="m-0 border-t border-divider pt-2.5 text-body-sm text-muted-600"
            >
              Loading itinerary preview…
            </p>
          )}
          {previewStatus === "error" && (
            <p
              role="status"
              className="m-0 border-t border-divider pt-2.5 text-body-sm text-muted-600"
            >
              Itinerary preview could not be loaded. Open the itinerary to try
              again.
            </p>
          )}
          {itineraryDays.map((day) => (
            <div
              key={day.id}
              className="flex gap-4 border-t border-divider py-2.5 first:border-t-0"
            >
              <span className="w-13 flex-none font-mono text-badge font-medium tracking-wider text-accent-700 uppercase">
                {day.label}
              </span>
              <span className="text-body-sm leading-relaxed text-muted-700">
                {day.stops}
              </span>
            </div>
          ))}
          {previewStatus === "empty" && (
            <p className="m-0 border-t border-divider pt-2.5 text-body-sm text-muted-600">
              No itinerary has been saved for this trip yet.
            </p>
          )}
        </div>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={() => onViewItinerary?.(trip)}
            className="rounded-pill bg-accent px-3.5 py-1.5 text-xs font-medium text-white shadow-control hover:bg-accent-600"
          >
            View itinerary
          </button>
          {!isSaved && onSave && (
            <>
              <button
                type="button"
                onClick={() => onSave?.(trip)}
                disabled={actionPending}
                className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {actionPending ? "Saving…" : "Save trip"}
              </button>
              <button
                type="button"
                onClick={() => onKeepRefining?.(trip)}
                className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
              >
                Keep refining
              </button>
            </>
          )}
          {isSaved && onUnsave && (
            <button
              type="button"
              onClick={() => onUnsave?.(trip)}
              disabled={actionPending}
              className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {actionPending ? "Unsaving…" : "Unsave"}
            </button>
          )}
          <button
            type="button"
            className="ml-auto rounded-pill px-3.5 py-1.5 text-xs font-medium text-muted-700 hover:bg-bg"
          >
            Share
          </button>
        </div>
      </div>
    </article>
  );
}

export default GeneratedTripCard;
