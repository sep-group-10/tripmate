const METER_COLORS = ["#e8532b", "#2f6ff0"];

/** A ranked list of labeled progress bars (e.g. "popular destinations"
 * by rating/share). The top entry gets the accent color, the rest the
 * secondary info color, matching the design system's two-series meters. */
function BarMeterList({ items, emptyLabel }) {
  if (items.length === 0) {
    return <p className="text-helper text-muted-600">{emptyLabel}</p>;
  }

  return (
    <div className="flex flex-col gap-3">
      {items.map((item, index) => (
        <div key={item.id} className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between gap-3">
            <span className="text-body-sm font-medium text-ink">
              {item.label}
            </span>
            <span className="text-helper text-muted-600">{item.note}</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-pill bg-bg">
            <div
              className="h-full rounded-pill"
              style={{
                width: `${item.pct}%`,
                backgroundColor: METER_COLORS[index === 0 ? 0 : 1],
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default BarMeterList;
