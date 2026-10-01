import { useState } from "react";
import { TRIP_DUMMY } from "../../data/tripPlanDummyData";
import BudgetTab from "./BudgetTab";
import EmptyState from "./EmptyState";
import ItineraryTab from "./ItineraryTab";
import MapTab from "./MapTab";
import SummaryTab from "./SummaryTab";
import { TAB_EMPTY_STATES } from "./tabEmptyStates";

// Tab order. The active tab always starts as Summary.
const TABS = ["Summary", "Map", "Itinerary", "Budget"];

// `itinerary` is the ChatItinerary from the latest plan (null before one exists).
// Itinerary and Map render it. Summary and Budget have no backend data yet (the
// response carries no hero facts, trade-offs or costs), so they show TRIP_DUMMY
// whenever a plan exists. Swap `trip` for real data once an endpoint provides it.
// `onLoadSample` is passed in development only (see TripPlanChatPage); it adds a
// "Load sample trip" button to the empty state.
function TabsPanel({ itinerary, onLoadSample }) {
  const [tab, setTab] = useState("Summary");
  const trip = itinerary ? TRIP_DUMMY : null;

  return (
    <section
      aria-label="Trip details"
      className="flex min-h-0 flex-col overflow-hidden rounded-panel bg-surface shadow-control"
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
        {!itinerary && (
          <EmptyState {...TAB_EMPTY_STATES[tab]}>
            {import.meta.env.DEV && onLoadSample && (
              <button
                type="button"
                onClick={onLoadSample}
                className="rounded-pill border border-border bg-surface px-3.25 py-1.75 text-[13px] font-medium text-ink shadow-control"
              >
                Load sample trip
              </button>
            )}
          </EmptyState>
        )}
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
