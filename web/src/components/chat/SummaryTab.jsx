import PillTag from "./PillTag";
import SectionLabel from "./SectionLabel";
import TripHero from "./TripHero";

const TRADEOFF_PILLS = {
  swapped: { label: "Swapped", tone: "info" },
  kept: { label: "Kept", tone: "success" },
  dropped: { label: "Dropped", tone: "warn" },
};

function SummaryTab({ summary }) {
  return (
    <>
      <TripHero summary={summary} />

      <div className="flex flex-none flex-col gap-2 rounded-xl bg-inset p-4.5">
        <SectionLabel>What TripMate optimised for</SectionLabel>
        <p className="m-0 text-sm leading-[1.62] text-muted-700">
          {summary.optimised_for}
        </p>
      </div>

      <div className="flex flex-none flex-col">
        <SectionLabel>Trade-offs it made</SectionLabel>
        <div className="mt-2.5 flex flex-col">
          {summary.tradeoffs.map((item) => {
            const pill = TRADEOFF_PILLS[item.type] ?? TRADEOFF_PILLS.kept;
            return (
              <div
                key={item.text}
                className="flex items-start gap-3 border-t border-divider py-3"
              >
                <PillTag tone={pill.tone}>{pill.label}</PillTag>
                <span className="text-body-sm leading-[1.55] text-muted-700">
                  {item.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}

export default SummaryTab;
