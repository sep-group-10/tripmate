/** Single stat tile used in admin KPI rows: a label, a big number, and a
 * short note underneath. `accent` colors the value in the brand accent
 * for the one metric that should draw the eye (e.g. a highlight count). */
function KpiCard({ label, value, note, accent = false }) {
  return (
    <div className="flex flex-col gap-2 rounded-card bg-surface p-5 shadow-control">
      <span className="text-label font-medium text-muted-600">{label}</span>
      <span
        className={`font-heading text-[30px] font-semibold tracking-tight ${
          accent ? "text-accent" : "text-ink"
        }`}
      >
        {value}
      </span>
      <span className="text-helper text-muted-600">{note}</span>
    </div>
  );
}

export default KpiCard;
