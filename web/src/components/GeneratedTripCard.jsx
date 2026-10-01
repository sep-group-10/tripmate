import { useEffect, useRef, useState } from "react";
import { TRIP_STATUS } from "../constants/tripStatus";
import { PILL_TONES } from "../utils/pillTones";

// GENERATED is informational (blue) so it stays distinct from the green SAVED.
const STATUS_PILLS = {
  [TRIP_STATUS.GENERATED]: { label: "Generated", tone: PILL_TONES.info },
  [TRIP_STATUS.SAVED]: { label: "Saved", tone: PILL_TONES.success },
};

/** The "···" button on a card's cover, opening a small menu of `items`
 * ({ label, onSelect }). Closes on an outside click or Escape. */
function TripActionsMenu({ items }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const handlePointerDown = (event) => {
      if (!ref.current?.contains(event.target)) setOpen(false);
    };
    const handleKeyDown = (event) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <div ref={ref} className="absolute top-3.5 right-3.5">
      <button
        type="button"
        aria-label="Trip actions"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
        className="flex h-8 w-8 items-center justify-center rounded-pill bg-white/90 text-muted-700"
      >
        ···
      </button>
      {open && (
        <div
          role="menu"
          className="absolute right-0 z-10 mt-1.5 min-w-44 rounded-lg border border-border bg-surface p-1 shadow-raised"
        >
          {items.map((item) => (
            <button
              key={item.label}
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false);
                item.onSelect();
              }}
              className="w-full rounded-md px-3 py-2 text-left text-body-sm text-ink hover:bg-bg"
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/** Card for a completed itinerary (GENERATED or SAVED): cover photo with
 * overlaid title, a quick-facts strip, a day-by-day summary and actions.
 * A generated trip can be saved (`onSave`); a saved trip can be removed from
 * saved (`onUnsave`) from the "···" menu. */
function GeneratedTripCard({ trip, onSave, onUnsave }) {
  const isSaved = trip.status === TRIP_STATUS.SAVED;
  const pill = STATUS_PILLS[trip.status] ?? STATUS_PILLS[TRIP_STATUS.GENERATED];

  return (
    <article className="flex flex-col overflow-hidden rounded-card bg-surface shadow-control">
      <div className="relative h-50">
        {trip.coverImageUrl ? (
          <img
            src={trip.coverImageUrl}
            alt=""
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-[repeating-linear-gradient(135deg,var(--color-bg)_0_7px,rgba(23,25,26,0.05)_7px_8px)] font-mono text-caption tracking-wider text-muted-500 uppercase">
            {trip.coverHint}
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 via-45% to-transparent to-70%" />
        <span
          className={`absolute top-4 left-4 rounded-pill px-2.5 py-1 text-caption font-medium ${pill.tone}`}
        >
          {pill.label}
        </span>
        {isSaved ? (
          <TripActionsMenu
            items={[
              { label: "Remove from saved", onSelect: () => onUnsave?.(trip) },
            ]}
          />
        ) : (
          <button
            type="button"
            aria-label="Trip actions"
            className="absolute top-3.5 right-3.5 flex h-8 w-8 items-center justify-center rounded-pill bg-white/90 text-muted-700"
          >
            ···
          </button>
        )}
        <div className="absolute bottom-4 left-5 flex flex-col gap-0.5">
          <span className="font-mono text-caption tracking-widest text-white/80 uppercase">
            {trip.where}
          </span>
          <h3 className="font-heading text-xl font-semibold tracking-tight text-white">
            {trip.title}
          </h3>
        </div>
      </div>

      <div className="flex flex-col gap-4 p-5.5">
        <div className="grid grid-cols-2 gap-3.5 rounded-lg bg-bg p-4 sm:grid-cols-4">
          {trip.facts.map((fact) => (
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
          {trip.days.map((day) => (
            <div
              key={day.label}
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
        </div>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            className="rounded-pill bg-accent px-3.5 py-1.5 text-xs font-medium text-white shadow-control hover:bg-accent-600"
          >
            View itinerary
          </button>
          {!isSaved && (
            <>
              <button
                type="button"
                onClick={() => onSave?.(trip)}
                className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
              >
                Save trip
              </button>
              <button
                type="button"
                className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
              >
                Keep refining
              </button>
            </>
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
