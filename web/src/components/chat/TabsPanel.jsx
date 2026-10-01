import { useState } from "react";
import { TRIP_DUMMY } from "../../data/tripPlanDummyData";
import BudgetTab from "./BudgetTab";
import EmptyState from "./EmptyState";
import ItineraryTab from "./ItineraryTab";
import MapTab from "./MapTab";
import SummaryTab from "./SummaryTab";

const TABS = ["Summary", "Map", "Itinerary", "Budget"];

// `itinerary` is the ChatItinerary from the latest plan (null before one exists).
// Itinerary and Map render it. Summary and Budget have no backend data yet (the
// response carries no hero facts, trade-offs or costs), so they show TRIP_DUMMY
// whenever a plan exists. Swap `trip` for real data once an endpoint provides it.
function TabsPanel({ itinerary }) {
  const [tab, setTab] = useState("Summary");
  const trip = itinerary ? TRIP_DUMMY : null;

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
        {!itinerary && <EmptyState what="itinerary" />}
        {itinerary && tab === "Summary" && (
          <SummaryTab summary={trip.summary} />
        )}
        {itinerary && tab === "Map" && <MapTab itinerary={itinerary} />}
        {itinerary && tab === "Itinerary" && (
          <ItineraryTab itinerary={itinerary} />
        )}
        {itinerary && tab === "Budget" && (
          <BudgetTab summary={trip.summary} budget={trip.budget} />
        )}
      </div>
    </section>
  );
}

export default TabsPanel;
