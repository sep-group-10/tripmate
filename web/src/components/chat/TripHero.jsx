import { formatDateRange, tripDurationDays } from "../../utils/tripFormat";
import SectionLabel from "./SectionLabel";

// Shared header for the Summary and Budget tabs: the dark hero card and the
// facts row beneath it. `summary` is the trip summary object (see
// data/tripPlanDummyData.js for its shape).
function TripHero({ summary }) {
  const days = tripDurationDays(summary.start_date, summary.end_date);
  const facts = [
    { label: "Duration", value: `${days} ${days === 1 ? "day" : "days"}` },
    {
      label: "Travellers",
      value: `${summary.travellers} ${summary.travellers === 1 ? "traveller" : "travellers"}`,
    },
    {
      label: "Dates",
      value: formatDateRange(summary.start_date, summary.end_date),
    },
    { label: "Pace", value: summary.pace },
  ];

  return (
    <>
      <div className="flex-none rounded-2xl bg-muted-900 p-px shadow-card">
        <div className="flex flex-col gap-1.5 rounded-[15px] p-5.75 shadow-[inset_0_1px_0_rgba(255,255,255,0.12),inset_0_0_0_1px_rgba(255,255,255,0.05)]">
          <div className="flex items-start gap-3">
            <span className="min-w-0 flex-1 font-mono text-[10.5px] tracking-widest text-accent-300 uppercase">
              {summary.route_label}
            </span>
            <span className="flex-none rounded-pill bg-white/12 px-2.5 py-1 text-caption font-medium text-white">
              Generated today
            </span>
          </div>
          <h2 className="font-heading m-0 mt-0.5 max-w-[22ch] text-2xl font-semibold tracking-[-0.025em] text-balance text-white">
            {summary.title}
          </h2>
          <div className="mt-3 flex items-center gap-2.5 border-t border-white/10 pt-3.5 text-label text-white/62">
            <span>{summary.occasion}</span>
            <span className="text-white/30">·</span>
            <span className="tabular-nums">
              {formatDateRange(summary.start_date, summary.end_date, {
                withYear: true,
              })}
            </span>
            <span className="font-heading ml-auto text-[15px] font-semibold text-accent-300 tabular-nums">
              {summary.stop_count} stops
            </span>
          </div>
        </div>
      </div>

      <div className="grid flex-none grid-cols-[repeat(auto-fit,minmax(120px,1fr))] overflow-hidden rounded-xl bg-inset">
        {facts.map((fact) => (
          <div key={fact.label} className="flex flex-col gap-1 px-4 py-3.5">
            <SectionLabel>{fact.label}</SectionLabel>
            <span className="text-[16px] font-semibold tabular-nums">
              {fact.value}
            </span>
          </div>
        ))}
      </div>
    </>
  );
}

export default TripHero;
