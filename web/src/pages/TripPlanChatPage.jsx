// Trip-plan page, still on dummy data with no real API. Chat panel on the left,
// tabs panel on the right (Summary, Map, Itinerary, Budget). Session list and
// mobile layout come in later steps. The pieces live in components/chat/ and the
// placeholder content in data/tripPlanDummyData.js.
import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";
import ChatPanel from "../components/chat/ChatPanel";
import TabsPanel from "../components/chat/TabsPanel";

function TripPlanChatPage() {
  return (
    <div className="font-body flex h-screen flex-col bg-bg text-ink">
      <header className="flex items-center gap-2.5 px-6 py-4">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="flex h-logo w-logo items-center justify-center rounded-lg bg-accent text-white">
            <MapPin size={15} aria-hidden="true" />
          </span>
          <span className="font-heading text-md font-semibold tracking-tight">
            TripMate
          </span>
        </Link>
        <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
          Trip planner
        </span>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] grid-rows-[minmax(0,1fr)] gap-3.5 px-6 pb-6">
        <ChatPanel />

        <TabsPanel />
      </main>
    </div>
  );
}

export default TripPlanChatPage;
