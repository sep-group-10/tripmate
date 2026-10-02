const DELTA_CLASSES = {
  up: "text-success",
  down: "text-danger",
  flat: "text-muted-500",
};

/** A single surface split into equal stat columns by hairlines, each with
 * a label, a big number, and a colored delta note underneath. */
function StatRow({ stats }) {
  return (
    <section className="grid grid-cols-2 overflow-hidden rounded-card bg-surface shadow-control sm:grid-cols-4">
      {stats.map((stat, index) => (
        <div
          key={stat.label}
          className={`flex flex-col gap-1 p-5 ${
            index > 0 ? "border-t border-border sm:border-t-0 sm:border-l" : ""
          }`}
        >
          <span className="text-label font-medium text-muted-600">
            {stat.label}
          </span>
          <span className="font-heading text-[26px] font-semibold tracking-tight tabular-nums text-ink">
            {stat.value}
          </span>
          <span
            className={`text-helper font-medium ${DELTA_CLASSES[stat.deltaTone] || DELTA_CLASSES.flat}`}
          >
            {stat.delta}
          </span>
        </div>
      ))}
    </section>
  );
}

export default StatRow;
