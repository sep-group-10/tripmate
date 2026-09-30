import { useState } from "react";
import BudgetTab from "./BudgetTab";
import ItineraryTab from "./ItineraryTab";
import MapTab from "./MapTab";
import SummaryTab from "./SummaryTab";

const TABS = ["Summary", "Map", "Itinerary", "Budget"];

// `itinerary` is the ChatItinerary from the latest plan (null before one exists).
// Only the Itinerary and Map tabs read it so far; Summary and Budget still show
// dummy data because the response has no hero facts or costs yet.
function TabsPanel({ itinerary }) {
  const [tab, setTab] = useState("Summary");

  return (
    <section
      aria-label="Trip details"
      className="flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-surface shadow-control"
    >
      <div
        role="tablist"
        aria-label="Trip details"
        className="flex gap-1 border-b border-divider px-4.5 pt-3"
      >
        {TABS.map((label) => (
          <button
            key={label}
            id={`tab-${label}`}
            type="button"
            role="tab"
            aria-selected={tab === label}
            aria-controls="trip-tabpanel"
            onClick={() => setTab(label)}
            className={`-mb-px border-b-2 px-3.5 py-2.25 text-sm ${
              tab === label
                ? "border-accent font-semibold text-ink"
                : "border-transparent text-muted-600"
            }`}
          >
            {label}
          </button>
        ))}
      </div>
      <div
        id="trip-tabpanel"
        role="tabpanel"
        aria-labelledby={`tab-${tab}`}
        className="flex min-h-0 flex-1 flex-col gap-3.5 overflow-y-auto p-4.5"
      >
        {tab === "Summary" && <SummaryTab />}
        {tab === "Itinerary" && <ItineraryTab itinerary={itinerary} />}
        {tab === "Map" && <MapTab itinerary={itinerary} />}
        {tab === "Budget" && <BudgetTab />}
      </div>
    </section>
  );
}

export default TabsPanel;
