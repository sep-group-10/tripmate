// Step 1 of the trip-plan build: chat panel only, no real API. The tabs panel
// (Summary/Map/Itinerary/Budget), session list and mobile layout come in later steps.
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, SendHorizontal } from "lucide-react";

const SUGGESTIONS = ["Swap a day", "Cut LKR 40,000", "Add a beach night"];

const REPLY_DELAY_MS = 1000;

// Dummy content is shaped loosely like ChatItineraryDay / ChatItineraryItem
// (backend/app/schemas/chat.py) so it can be swapped for a real ChatResponse.
// `stops` are place names (in a real response, itinerary items[].name) and
// `actions` are short follow-up prompts shown under an assistant message.
const INITIAL_MESSAGES = [
  {
    id: "m1",
    role: "assistant",
    text: "Hi! Tell me where you'd like to go, for how long and what you enjoy, and I'll sketch a plan. Here's a sample of what a day can look like:",
    stops: ["Old Town", "Harbour market", "Castle hill"],
    actions: ["Make it cheaper", "Add a rest day", "Regenerate Day 1"],
    itineraryDay: {
      day_number: 1,
      date: "2026-10-12",
      items: [
        {
          candidate_id: "attr-1",
          category: "attraction",
          name: "Old Town walking tour",
          start_time: "09:30",
          end_time: "11:30",
        },
        {
          candidate_id: "rest-1",
          category: "restaurant",
          name: "Lunch at the harbour market",
          start_time: "12:00",
          end_time: "13:15",
        },
        {
          candidate_id: "attr-2",
          category: "attraction",
          name: "Castle hill viewpoint",
          start_time: "14:00",
          end_time: "16:00",
        },
      ],
    },
  },
  {
    id: "m2",
    role: "user",
    text: "Plan 3 days in Lisbon for two, we love food and walking.",
  },
];

const DUMMY_REPLIES = [
  "Got it - I'll keep that in mind and rework the plan around it. (Placeholder reply, no AI is connected yet.)",
  "Sure, I can adjust that. (Placeholder reply, no AI is connected yet.)",
  "Noted! Anything else you'd like to change? (Placeholder reply, no AI is connected yet.)",
];

function ItineraryPreview({ day }) {
  return (
    <div className="mt-3 rounded-lg bg-bg p-3.5">
      <span className="text-eyebrow font-medium tracking-wide text-muted-600 uppercase">
        Day {day.day_number} · {day.date}
      </span>
      <ul className="m-0 mt-2 flex list-none flex-col gap-2 p-0">
        {day.items.map((item) => (
          <li key={item.candidate_id} className="flex items-baseline gap-3">
            <span className="w-25 flex-none font-mono text-caption text-muted-600">
              {item.start_time}–{item.end_time}
            </span>
            <span className="text-body-sm">{item.name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MessageBubble({ message, onAction }) {
  const isUser = message.role === "user";
  return (
    <div
      className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}
    >
      <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
        {isUser ? "You" : "TripMate"}
      </span>
      <div
        className={`max-w-[86%] px-4 py-3.5 text-[14.5px] leading-[1.62] ${
          isUser
            ? "rounded-[16px_16px_4px_16px] bg-muted-900 text-white"
            : "rounded-[16px_16px_16px_4px] border border-border bg-inset text-ink"
        }`}
      >
        <p className="m-0">{message.text}</p>
        {message.itineraryDay && (
          <ItineraryPreview day={message.itineraryDay} />
        )}
        {message.stops?.length > 0 && (
          // Display-only for now: these become real buttons once the
          // Itinerary/Map tabs exist and a stop can be focused there.
          <div className="mt-3 flex flex-wrap gap-1.5">
            {message.stops.map((stop) => (
              <span
                key={stop}
                className="rounded-pill bg-success-100 px-2.5 py-1 text-caption font-medium text-success-700"
              >
                {stop}
              </span>
            ))}
          </div>
        )}
      </div>
      {message.actions?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {message.actions.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => onAction(action)}
              className="rounded-pill bg-accent-100 px-3.25 py-1.75 text-[13px] font-medium text-accent-700"
            >
              {action}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div
      className="flex items-center gap-2.5 text-body-sm text-muted-600"
      role="status"
    >
      <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />
      <span>TripMate is thinking…</span>
    </div>
  );
}

function SuggestionChip({ label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control"
    >
      {label}
    </button>
  );
}

function TripPlanChatPage() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const replyTimer = useRef(null);
  const replyCount = useRef(0);
  const listEndRef = useRef(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  useEffect(() => () => clearTimeout(replyTimer.current), []);

  const canSend = input.trim().length > 0 && !thinking;

  const handleSend = (event) => {
    event.preventDefault();
    if (!canSend) return;

    const text = input.trim();
    setMessages((prev) => [
      ...prev,
      { id: `u-${Date.now()}`, role: "user", text },
    ]);
    setInput("");
    setThinking(true);

    replyTimer.current = setTimeout(() => {
      const reply = DUMMY_REPLIES[replyCount.current % DUMMY_REPLIES.length];
      replyCount.current += 1;
      setMessages((prev) => [
        ...prev,
        { id: `a-${Date.now()}`, role: "assistant", text: reply },
      ]);
      setThinking(false);
    }, REPLY_DELAY_MS);
  };

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

      <main className="flex min-h-0 flex-1 justify-center px-6 pb-6">
        <section
          aria-label="Trip planning chat"
          className="flex min-h-0 w-full max-w-190 flex-col overflow-hidden rounded-[14px] bg-surface shadow-control"
        >
          <div className="flex min-h-0 flex-1 flex-col gap-4.5 overflow-y-auto p-5.5">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onAction={setInput}
              />
            ))}
            {thinking && <TypingIndicator />}
            <div ref={listEndRef} />
          </div>

          <div className="flex flex-col gap-3 border-t border-divider p-4">
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((label) => (
                <SuggestionChip
                  key={label}
                  label={label}
                  onClick={() => setInput(label)}
                />
              ))}
            </div>
            <form onSubmit={handleSend} className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask for a change — 'swap Day 3 for something quieter'"
                aria-label="Message"
                className="min-h-10 flex-1 rounded-pill border border-border bg-surface px-4 py-2 text-sm text-ink shadow-inset outline-none"
              />
              <button
                type="submit"
                disabled={!canSend}
                aria-label="Send message"
                className="flex h-9.5 w-9.5 flex-none items-center justify-center rounded-full bg-accent text-white disabled:cursor-not-allowed disabled:bg-muted-400"
              >
                <SendHorizontal size={16} aria-hidden="true" />
              </button>
            </form>
          </div>
        </section>
      </main>
    </div>
  );
}

export default TripPlanChatPage;
