// Trip-plan page. The chat panel talks to the real /chat endpoint, the
// Itinerary and Map tabs render the plan it returns, and Summary and Budget
// show placeholder content from data/tripPlanDummyData.js. Session list and
// mobile layout come in later steps. The pieces live in components/chat/.
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import ChatPanel from "../components/chat/ChatPanel";
import TabsPanel from "../components/chat/TabsPanel";
import { DEMO_ITINERARY } from "../data/tripPlanDummyData";

function TripPlanChatPage() {
  // Owned here so the chat (which produces plans) and the tabs (which show
  // them) can share it. Bumping chatKey remounts ChatPanel, which resets its
  // messages and session id.
  // Development only: ?demo=1 starts with the sample trip loaded so the Summary
  // and Budget tabs can be previewed without a real plan. import.meta.env.DEV is
  // false in production builds, so this and the sample data are dropped there.
  const [searchParams] = useSearchParams();
  const [itinerary, setItinerary] = useState(() =>
    import.meta.env.DEV && searchParams.get("demo") === "1"
      ? DEMO_ITINERARY
      : null,
  );
  const [chatKey, setChatKey] = useState(0);

  const loadSampleTrip = import.meta.env.DEV
    ? () => setItinerary(DEMO_ITINERARY)
    : undefined;

  const handleNewTrip = () => {
    setItinerary(null);
    setChatKey((key) => key + 1);
  };

  return (
    <div className="font-body flex min-h-0 flex-1 flex-col bg-bg text-ink">
      <header className="flex items-center gap-2.5 px-6 py-4">
        <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
          Trip planner
        </span>
        <button
          type="button"
          onClick={handleNewTrip}
          className="ml-auto rounded-pill border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control"
        >
          New trip
        </button>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] grid-rows-[minmax(0,1fr)] gap-3.5 px-6 pb-6">
        <ChatPanel key={`chat-${chatKey}`} onPlan={setItinerary} />

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
