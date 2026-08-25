const TAG_TONE_CLASSES = {
  accent: "bg-accent-100 text-accent-700",
  warn: "bg-warn-100 text-warn",
  info: "bg-info-100 text-info",
  success: "bg-success-100 text-success",
};

/** Shared admin list card: name/location/rating header, a tone-coded tag,
 * a description, a metrics row, optional chips (e.g. amenities), and the
 * standard Edit/Preview/Delete row. Used by all 4 entity lists in C3.1 so
 * the layout isn't duplicated per entity. */
function EntityCard({
  name,
  location,
  rating,
  tag,
  description,
  metrics = [],
  chips,
  onEdit,
  onDelete,
}) {
  return (
    <article className="flex flex-col gap-3 rounded-lg bg-surface p-5 shadow-control">
      <div className="flex items-start gap-3">
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <h3 className="font-heading m-0 text-base font-semibold tracking-tight">
            {name}
          </h3>
          <span className="text-label text-muted-600">{location}</span>
        </div>
        {rating != null && (
          <span className="flex flex-none items-center gap-1 text-label font-medium text-accent">
            ★ {rating}
          </span>
        )}
      </div>

      {tag && (
        <span
          className={`self-start rounded-full px-2.5 py-1 text-xs font-medium ${TAG_TONE_CLASSES[tag.tone] || TAG_TONE_CLASSES.accent}`}
        >
          {tag.label}
        </span>
      )}

      <p className="m-0 text-body-sm leading-relaxed text-muted-700">
        {description}
      </p>

      {metrics.length > 0 && (
        <div className="grid grid-cols-2 gap-x-4 gap-y-3 rounded-lg bg-bg p-3.5">
          {metrics.map((metric) => (
            <div key={metric.label} className="flex flex-col gap-0.5">
              <span className="text-eyebrow font-medium tracking-wide text-muted-600 uppercase">
                {metric.label}
              </span>
              <span className="text-body-sm">{metric.value}</span>
            </div>
          ))}
        </div>
      )}

      {chips && chips.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {chips.map((chip) => (
            <span
              key={chip}
              className="rounded-full border border-border px-2 py-0.5 text-caption text-muted-700"
            >
              {chip}
            </span>
          ))}
        </div>
      )}

      <div className="mt-auto flex gap-2 pt-1">
        <button
          type="button"
          onClick={onEdit}
          className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control"
        >
          Edit
        </button>
        <button
          type="button"
          className="rounded-full px-3.5 py-1.5 text-xs font-medium text-muted-700"
        >
          Preview
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="ml-auto rounded-full px-3.5 py-1.5 text-xs font-medium text-danger"
        >
          Delete
        </button>
      </div>
    </article>
  );
}

export default EntityCard;
