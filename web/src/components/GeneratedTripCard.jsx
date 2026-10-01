/** Card for a completed itinerary: cover photo with overlaid title, a
 * quick-facts strip, a day-by-day summary, and view/refine/share actions. */
function GeneratedTripCard({ trip }) {
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
        <span className="absolute top-4 left-4 rounded-pill bg-success-100 px-2.5 py-1 text-caption font-medium text-success-700">
          Generated
        </span>
        <button
          type="button"
          aria-label="Trip actions"
          className="absolute top-3.5 right-3.5 flex h-8 w-8 items-center justify-center rounded-pill bg-white/90 text-muted-700"
        >
          ···
        </button>
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
          <button
            type="button"
            className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
          >
            Keep refining
          </button>
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
