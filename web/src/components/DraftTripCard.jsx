const STAGE_BAR_COLORS = {
  "Collecting preferences": "bg-warn",
  "Choosing hotels": "bg-info",
  "Budget optimisation": "bg-accent",
};

/** Card for an in-progress planning session: stage pill, progress bar,
 * the prompt that started it, and actions to resume/rename/discard. */
function DraftTripCard({ trip }) {
  const barColor = STAGE_BAR_COLORS[trip.stage] || "bg-muted-300";

  return (
    <article className="flex overflow-hidden rounded-card bg-surface shadow-control">
      <span className={`w-1 flex-none ${barColor}`} />
      <div className="flex min-w-0 flex-1 flex-col gap-3.5 p-5.5">
        <div className="flex items-start gap-3">
          <div className="flex min-w-0 flex-1 flex-col gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-pill bg-warn-100 px-2.5 py-1 text-caption font-medium text-warn">
                Draft
              </span>
              <span className="font-mono text-badge font-medium tracking-wider text-muted-600 uppercase">
                {trip.stage}
              </span>
            </div>
            <h3 className="font-heading text-md font-semibold tracking-tight text-ink">
              {trip.title}
            </h3>
            <div className="flex flex-wrap items-center gap-2 text-label text-muted-600">
              <span>{trip.where}</span>
              <span className="text-muted-400">·</span>
              <span>Edited {trip.edited}</span>
            </div>
          </div>
          <button
            type="button"
            aria-label="Trip actions"
            className="flex h-8 w-8 flex-none items-center justify-center rounded-pill text-muted-600 hover:bg-bg"
          >
            ···
          </button>
        </div>

        <p className="m-0 border-l-2 border-muted-300 pl-3.5 text-body-sm leading-relaxed text-muted-700 italic">
          {trip.prompt}
        </p>

        <div className="flex flex-col gap-2">
          <span className="block h-1.5 overflow-hidden rounded-pill bg-bg">
            <span
              className="block h-full rounded-pill bg-accent"
              style={{ width: `${trip.pct}%` }}
            />
          </span>
          <div className="flex justify-between font-mono text-badge tracking-wider text-muted-500 uppercase">
            <span>Started</span>
            <span className="tabular-nums">{trip.pct}% complete</span>
            <span>Generated</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
          >
            Continue planning
          </button>
          <button
            type="button"
            className="rounded-pill px-3.5 py-1.5 text-xs font-medium text-muted-700 hover:bg-bg"
          >
            Rename
          </button>
          <button
            type="button"
            className="ml-auto rounded-pill px-3.5 py-1.5 text-xs font-medium text-danger hover:bg-danger-100"
          >
            Discard
          </button>
        </div>
      </div>
    </article>
  );
}

export default DraftTripCard;
