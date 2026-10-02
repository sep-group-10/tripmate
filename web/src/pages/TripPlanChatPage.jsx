// Trip-plan page. The chat panel talks to the real /chat endpoint, the
// Itinerary and Map tabs render the plan it returns, and Summary and Budget
// show placeholder content from data/tripPlanDummyData.js. Session list and
// mobile layout come in later steps. The pieces live in components/chat/.
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import ChatPanel from "../components/chat/ChatPanel";
import SaveTripButton from "../components/chat/SaveTripButton";
import TabsPanel from "../components/chat/TabsPanel";
import { TRIP_STATUS } from "../constants/tripStatus";
import { DEMO_ITINERARY } from "../data/tripPlanDummyData";
import { statusAfterSave } from "../utils/tripStatus";

function TripPlanChatPage() {
  // Owned here so the chat (which produces plans) and the tabs (which show
  // them) can share it. Bumping chatKey remounts ChatPanel, which resets its
  // messages and session id.
  // Development only: ?demo=1 starts with the sample trip loaded so the Summary
  // and Budget tabs can be previewed without a real plan. import.meta.env.DEV is
  // false in production builds, so this and the sample data are dropped there.
  const [searchParams] = useSearchParams();
  const startWithSample =
    import.meta.env.DEV && searchParams.get("demo") === "1";
  const [itinerary, setItinerary] = useState(() =>
    startWithSample ? DEMO_ITINERARY : null,
  );
  // Trip lifecycle (constants/tripStatus.js): DRAFT until a plan arrives,
  // GENERATED once it has, SAVED after "Save trip". A SAVED trip stays SAVED
  // when the chat refines it. The sample trip counts as GENERATED.
  // TODO(backend): once /chat returns the trip id, save with saveTrip(tripId).
  const [tripStatus, setTripStatus] = useState(
    startWithSample ? TRIP_STATUS.GENERATED : TRIP_STATUS.DRAFT,
  );
  const [chatKey, setChatKey] = useState(0);

  const handlePlan = (nextItinerary) => {
    setItinerary(nextItinerary);
    setTripStatus((status) =>
      status === TRIP_STATUS.SAVED ? status : TRIP_STATUS.GENERATED,
    );
  };

  const loadSampleTrip = import.meta.env.DEV
    ? () => handlePlan(DEMO_ITINERARY)
    : undefined;

  const handleSaveTrip = () => {
    try {
      setTripStatus(statusAfterSave(tripStatus));
      toast.success("Trip saved");
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleNewTrip = () => {
    setItinerary(null);
    setTripStatus(TRIP_STATUS.DRAFT);
    setChatKey((key) => key + 1);
  };

  return (
    <div className="font-body flex min-h-0 flex-1 flex-col bg-bg text-ink">
      <header className="flex items-center gap-2.5 px-6 py-4">
        <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
          Trip planner
        </span>
        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            onClick={handleNewTrip}
            className="rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control"
          >
            New trip
          </button>
          <SaveTripButton status={tripStatus} onSave={handleSaveTrip} />
        </div>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] grid-rows-[minmax(0,1fr)] gap-3.5 px-6 pb-6">
        <ChatPanel key={`chat-${chatKey}`} onPlan={handlePlan} />

        {/* key resets the tab (back to Summary) on "New trip" */}
        <TabsPanel
          key={`tabs-${chatKey}`}
          itinerary={itinerary}
          onLoadSample={loadSampleTrip}
        />
      </main>
    </div>
  );
}

export default TripPlanChatPage;
