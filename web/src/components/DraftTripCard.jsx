import { useState } from "react";

const STAGE_BAR_COLORS = {
  "Collecting preferences": "bg-warn",
  "Choosing hotels": "bg-info",
  "Budget optimisation": "bg-accent",
};

/** Card for an in-progress planning session: stage pill, progress bar,
 * the prompt that started it, and actions to resume/rename/discard. */
function DraftTripCard({
  trip,
  onContinue,
  onRename,
  onDiscard,
  actionPending = false,
}) {
  const barColor = STAGE_BAR_COLORS[trip.stage] || "bg-muted-300";
  const [renaming, setRenaming] = useState(false);
  const [title, setTitle] = useState(trip.title || "");
  const [renameError, setRenameError] = useState("");

  const saveTitle = async (event) => {
    event.preventDefault();
    const nextTitle = title.trim();
    if (!nextTitle) {
      setRenameError("Enter a trip name.");
      return;
    }
    if (nextTitle.length > 255) {
      setRenameError("Trip names must be 255 characters or fewer.");
      return;
    }

    setRenameError("");
    const saved = await onRename?.(trip, nextTitle);
    if (saved) setRenaming(false);
    else setRenameError("The trip name could not be saved. Please try again.");
  };

  const discardTrip = async () => {
    const confirmed = window.confirm(
      `Discard “${trip.title || "Untitled trip"}”? This also deletes its planning conversation.`,
    );
    if (confirmed) await onDiscard?.(trip);
  };

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
            {renaming ? (
              <form
                onSubmit={saveTitle}
                className="flex flex-col items-start gap-1.5"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <input
                    autoFocus
                    aria-label="Trip name"
                    maxLength={255}
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    disabled={actionPending}
                    className="min-w-55 rounded-md border border-border bg-surface px-2.5 py-1.5 text-body-sm text-ink outline-none focus:border-accent"
                  />
                  <button
                    type="submit"
                    disabled={actionPending}
                    className="rounded-pill bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {actionPending ? "Saving…" : "Save name"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setTitle(trip.title || "");
                      setRenameError("");
                      setRenaming(false);
                    }}
                    disabled={actionPending}
                    className="rounded-pill px-3 py-1.5 text-xs font-medium text-muted-700 hover:bg-bg"
                  >
                    Cancel
                  </button>
                </div>
                {renameError && (
                  <span className="text-label text-danger" role="alert">
                    {renameError}
                  </span>
                )}
              </form>
            ) : (
              <h3 className="font-heading text-md font-semibold tracking-tight text-ink">
                {trip.title}
              </h3>
            )}
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

        {trip.prompt && (
          <p className="m-0 border-l-2 border-muted-300 pl-3.5 text-body-sm leading-relaxed text-muted-700 italic">
            {trip.prompt}
          </p>
        )}

        {trip.pct != null && (
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
        )}

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={() => onContinue?.(trip)}
            className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control hover:border-muted-400"
          >
            Continue planning
          </button>
          <button
            type="button"
            onClick={() => {
              setTitle(trip.title || "");
              setRenameError("");
              setRenaming(true);
            }}
            disabled={actionPending || renaming}
            className="rounded-pill px-3.5 py-1.5 text-xs font-medium text-muted-700 hover:bg-bg"
          >
            {actionPending && renaming ? "Saving…" : "Rename"}
          </button>
          <button
            type="button"
            onClick={discardTrip}
            disabled={actionPending}
            className="ml-auto rounded-pill px-3.5 py-1.5 text-xs font-medium text-danger hover:bg-danger-100"
          >
            {actionPending ? "Discarding…" : "Discard"}
          </button>
        </div>
      </div>
    </article>
  );
}

export default DraftTripCard;
