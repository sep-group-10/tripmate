// Trip-plan page. The chat panel talks to the real /chat endpoint, the
// Itinerary and Map tabs render the plan it returns, and Summary and Budget
// show placeholder content from data/tripPlanDummyData.js. Session list and
// mobile layout come in later steps. The pieces live in components/chat/.
import { useState } from "react";
import ChatPanel from "../components/chat/ChatPanel";
import TabsPanel from "../components/chat/TabsPanel";

function TripPlanChatPage() {
  // Owned here so the chat (which produces plans) and the tabs (which show
  // them) can share it. Bumping chatKey remounts ChatPanel, which resets its
  // messages and session id.
  const [itinerary, setItinerary] = useState(null);
  const [chatKey, setChatKey] = useState(0);

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
        <ChatPanel key={chatKey} onPlan={setItinerary} />

        <TabsPanel itinerary={itinerary} />
      </main>
    </div>
  );
}

export default TripPlanChatPage;
