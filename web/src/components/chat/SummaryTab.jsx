import {
  ITINERARY_DAYS,
  TRADEOFFS,
  TRIP_FACTS,
} from "../../data/tripPlanDummyData";
import { formatDate } from "../../utils/tripFormat";
import PillTag from "./PillTag";
import SectionLabel from "./SectionLabel";

function SummaryTab() {
  const stopCount = ITINERARY_DAYS.reduce((n, d) => n + d.items.length, 0);
  const first = formatDate(ITINERARY_DAYS[0].date);
  const last = formatDate(ITINERARY_DAYS.at(-1).date);
  const facts = [
    { label: "Duration", value: `${ITINERARY_DAYS.length} days` },
    { label: "Travellers", value: TRIP_FACTS.travellers },
    { label: "Dates", value: `${first}–${last.split(" ")[1]}` },
    { label: "Pace", value: TRIP_FACTS.pace },
  ];

  return (
    <>
      <div className="flex-none rounded-2xl bg-muted-900 p-px shadow-card">
        <div className="flex flex-col gap-1.5 rounded-[15px] p-5.75 shadow-[inset_0_1px_0_rgba(255,255,255,0.12),inset_0_0_0_1px_rgba(255,255,255,0.05)]">
          <div className="flex items-start gap-3">
            <span className="min-w-0 flex-1 font-mono text-[10.5px] tracking-widest text-accent-300 uppercase">
              {TRIP_FACTS.places}
            </span>
            <span className="flex-none rounded-pill bg-white/12 px-2.5 py-1 text-caption font-medium text-white">
              Generated today
            </span>
          </div>
          <h2 className="font-heading m-0 mt-0.5 max-w-[22ch] text-2xl font-semibold tracking-tight text-white">
            {TRIP_FACTS.title}
          </h2>
          <div className="mt-3 flex items-center gap-2.5 border-t border-white/10 pt-3.5 text-label text-white/60">
            <span>Food and walking</span>
            <span className="text-white/30">·</span>
            <span>
              {first}–{last.split(" ")[1]}, 2026
            </span>
            <span className="font-heading ml-auto text-[15px] font-semibold text-accent-300">
              {stopCount} stops
            </span>
          </div>
        </div>
      </div>

      <div className="grid flex-none grid-cols-[repeat(auto-fit,minmax(120px,1fr))] overflow-hidden rounded-xl bg-inset">
        {facts.map((fact) => (
          <div key={fact.label} className="flex flex-col gap-0.5 px-4 py-3.5">
            <span className="text-label text-muted-600">{fact.label}</span>
            <span className="text-md font-semibold">{fact.value}</span>
          </div>
        ))}
      </div>

      <div className="flex flex-none flex-col gap-2 rounded-xl bg-inset p-4.5">
        <SectionLabel>What TripMate optimised for</SectionLabel>
        <p className="m-0 text-sm leading-relaxed text-muted-700">
          Your plan keeps Day 1 walkable around Kandy — the Temple of the Sacred
          Tooth Relic, a local lunch and Kandy Lake sit within a few kilometres
          of each other. The long drive to Ella is on Day 2 with only light
          stops around it, and Day 3 is saved for Ella&apos;s two viewpoints so
          both land in clear morning and late-afternoon light.
        </p>
      </div>

      <div className="flex flex-none flex-col">
        <SectionLabel>Trade-offs it made</SectionLabel>
        {TRADEOFFS.map((item) => (
          <div
            key={item.tag}
            className="mt-2.5 flex items-start gap-3 border-t border-divider pt-3"
          >
            <PillTag tone={item.tone}>{item.tag}</PillTag>
            <span className="text-body-sm leading-relaxed text-muted-700">
              {item.text}
            </span>
          </div>
        ))}
      </div>
    </>
  );
}

export default SummaryTab;
