// Trip-plan page, still on dummy data with no real API. Chat panel on the left,
// tabs panel on the right (Summary + Itinerary built; Map and Budget are
// placeholders). Session list and mobile layout come in later steps.
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronUp, MapPin, SendHorizontal } from "lucide-react";

const SUGGESTIONS = ["Swap a day", "Cut LKR 40,000", "Add a beach night"];

const REPLY_DELAY_MS = 1000;

// Dummy itinerary, shaped like ChatItineraryDay / ChatItineraryItem
// (backend/app/schemas/chat.py): day_number, date, items[] with candidate_id,
// category, name, start_time, end_time, and route_optimization.local_distance_km.
// The real schema has NO costs, travel legs or day titles yet, so `cost` (EUR),
// `legs` (one per gap between items) and `title` below are dummy-only extras that
// the backend would need to add before this can be wired to a ChatResponse.
const ITINERARY_DAYS = [
  {
    day_number: 1,
    date: "2026-10-12",
    title: "Old Town & harbour",
    route_optimization: { local_distance_km: 3.2 },
    items: [
      {
        candidate_id: "attr-1",
        category: "attraction",
        name: "Old Town walking tour",
        start_time: "09:30",
        end_time: "11:30",
        cost: 30,
      },
      {
        candidate_id: "rest-1",
        category: "restaurant",
        name: "Lunch at the harbour market",
        start_time: "12:00",
        end_time: "13:15",
        cost: 28,
      },
      {
        candidate_id: "attr-2",
        category: "attraction",
        name: "Castle hill viewpoint",
        start_time: "14:00",
        end_time: "16:00",
        cost: 22,
      },
    ],
    legs: [
      { mode: "Walk", duration_minutes: 8, cost: 0 },
      { mode: "Tram", duration_minutes: 18, cost: 3 },
    ],
  },
  {
    day_number: 2,
    date: "2026-10-13",
    title: "Belém & the river",
    route_optimization: { local_distance_km: 7.4 },
    items: [
      {
        candidate_id: "attr-3",
        category: "attraction",
        name: "Belém Tower and monastery",
        start_time: "09:00",
        end_time: "12:00",
        cost: 24,
      },
      {
        candidate_id: "rest-2",
        category: "restaurant",
        name: "Pastel de nata tasting and lunch",
        start_time: "12:30",
        end_time: "14:00",
        cost: 26,
      },
      {
        candidate_id: "attr-4",
        category: "attraction",
        name: "Riverside sunset walk",
        start_time: "17:30",
        end_time: "19:00",
        cost: 0,
      },
    ],
    legs: [
      { mode: "Tram", duration_minutes: 22, cost: 3 },
      { mode: "Taxi", duration_minutes: 15, cost: 9 },
    ],
  },
  {
    day_number: 3,
    date: "2026-10-14",
    title: "Sintra day trip",
    route_optimization: { local_distance_km: 58 },
    items: [
      {
        candidate_id: "attr-5",
        category: "attraction",
        name: "Pena Palace",
        start_time: "09:30",
        end_time: "12:30",
        cost: 32,
      },
      {
        candidate_id: "rest-3",
        category: "restaurant",
        name: "Lunch in Sintra village",
        start_time: "13:00",
        end_time: "14:15",
        cost: 30,
      },
      {
        candidate_id: "attr-6",
        category: "attraction",
        name: "Cabo da Roca viewpoint",
        start_time: "16:00",
        end_time: "17:30",
        cost: 0,
      },
    ],
    legs: [
      { mode: "Bus", duration_minutes: 12, cost: 4 },
      { mode: "Bus", duration_minutes: 40, cost: 5 },
    ],
  },
];

const TRIP_FACTS = {
  title: "Three days of food and walking in Lisbon",
  places: "Lisbon · Belém · Sintra",
  travellers: "2 adults",
  pace: "Relaxed",
};

const TRADEOFFS = [
  {
    tag: "Swapped",
    tone: "info",
    text: "Belém moved to Day 2 morning — Day 1 afternoons showed long queues at the monastery, so the earlier slot avoids the crowd.",
  },
  {
    tag: "Kept",
    tone: "success",
    text: "The harbour market lunch stayed on Day 1 despite the detour: it's the best-rated food stop within walking distance of the Old Town tour.",
  },
  {
    tag: "Dropped",
    tone: "warn",
    text: "The Évora day trip — two hours each way doesn't fit a relaxed pace with two travellers.",
  },
];

// Mirrors EntityCard's TAG_TONE_CLASSES (private to that file) plus an outline
// tone; success uses success-700 for readable text at this size.
const PILL_TONES = {
  accent: "bg-accent-100 text-accent-700",
  info: "bg-info-100 text-info",
  success: "bg-success-100 text-success-700",
  warn: "bg-warn-100 text-warn",
  outline: "border border-border text-muted-700",
};

const CATEGORY_TAGS = {
  attraction: { label: "Attraction", tone: "info" },
  restaurant: { label: "Dining", tone: "warn" },
  hotel: { label: "Stay", tone: "outline" },
};

const TABS = ["Summary", "Map", "Itinerary", "Budget"];

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
    itineraryDay: ITINERARY_DAYS[0],
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

function formatDate(iso) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function formatMoney(amount, freeLabel = "Free") {
  return amount === 0 ? freeLabel : `€${amount.toLocaleString("en-US")}`;
}

function daySpend(day) {
  return [...day.items, ...day.legs].reduce((sum, row) => sum + row.cost, 0);
}

function SectionLabel({ children }) {
  return (
    <span className="font-mono text-badge font-medium tracking-wider text-muted-600 uppercase">
      {children}
    </span>
  );
}

function PillTag({ tone, children, className = "" }) {
  return (
    <span
      className={`flex-none rounded-pill px-2.5 py-1 text-caption font-medium ${PILL_TONES[tone] || PILL_TONES.outline} ${className}`}
    >
      {children}
    </span>
  );
}

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
          Your plan keeps every day walkable: the Old Town tour and harbour
          lunch sit together on Day 1, Belém gets a full morning before the
          crowds on Day 2, and the Sintra day trip is saved for Day 3 so the
          long transfer lands on a lighter schedule. Food stops are spread
          across all three days.
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

function ItineraryTab() {
  const [activeDay, setActiveDay] = useState(1);
  const [openDay, setOpenDay] = useState(1);

  const stopCount = ITINERARY_DAYS.reduce((n, d) => n + d.items.length, 0);
  const totalSpend = ITINERARY_DAYS.reduce((n, d) => n + daySpend(d), 0);

  const pickDay = (dayNumber) => {
    setActiveDay(dayNumber);
    setOpenDay(dayNumber);
    requestAnimationFrame(() =>
      document
        .getElementById(`itinerary-day-${dayNumber}`)
        ?.scrollIntoView({ behavior: "smooth", block: "nearest" }),
    );
  };

  const toggleDay = (dayNumber) => {
    setActiveDay(dayNumber);
    setOpenDay(openDay === dayNumber ? 0 : dayNumber);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end gap-4">
        <div className="flex min-w-0 flex-1 flex-col gap-0.5">
          <h2 className="font-heading m-0 text-[19px] font-semibold tracking-tight">
            {ITINERARY_DAYS.length}-day itinerary
          </h2>
          <span className="text-helper text-muted-600">
            {formatDate(ITINERARY_DAYS[0].date)} –{" "}
            {formatDate(ITINERARY_DAYS.at(-1).date)}, 2026
          </span>
        </div>
        <div className="flex items-center gap-3.5">
          <span className="text-helper text-muted-600">{stopCount} stops</span>
          <span className="text-body-sm font-semibold">
            {formatMoney(totalSpend)}
          </span>
        </div>
      </div>

      <div className="flex gap-0.5 overflow-x-auto py-0.5">
        {ITINERARY_DAYS.map((day) => {
          const on = activeDay === day.day_number;
          return (
            <button
              key={day.day_number}
              type="button"
              onClick={() => pickDay(day.day_number)}
              aria-label={`Go to day ${day.day_number}`}
              aria-current={on ? "step" : undefined}
              className="flex min-w-14 flex-1 flex-col items-center gap-1.5 px-1 py-2"
            >
              <span
                className={`flex h-7.5 w-7.5 items-center justify-center rounded-full border text-label font-semibold ${
                  on
                    ? "border-accent bg-accent text-white"
                    : "border-border bg-surface text-muted-600"
                }`}
              >
                {day.day_number}
              </span>
              <span
                className={`text-[11px] ${on ? "text-ink" : "text-muted-500"}`}
              >
                {formatDate(day.date)}
              </span>
            </button>
          );
        })}
      </div>

      <div className="flex flex-col gap-2.5">
        {ITINERARY_DAYS.map((day) => {
          const open = openDay === day.day_number;
          return (
            <section
              key={day.day_number}
              id={`itinerary-day-${day.day_number}`}
              className={`overflow-hidden rounded-[14px] border ${
                open ? "border-accent-200 bg-inset" : "border-border bg-surface"
              }`}
            >
              <button
                type="button"
                onClick={() => toggleDay(day.day_number)}
                aria-expanded={open}
                className="flex w-full flex-col gap-2 px-4.5 py-4 text-left"
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className={`h-2 w-2 flex-none rounded-full ${open ? "bg-accent" : "bg-muted-400"}`}
                  />
                  <span className="font-heading text-[15.5px] font-semibold tracking-tight">
                    Day {day.day_number}
                  </span>
                  <span className="text-label text-muted-600">
                    {formatDate(day.date)} · {day.title}
                  </span>
                  {open ? (
                    <ChevronUp
                      size={16}
                      className="ml-auto flex-none text-muted-600"
                      aria-hidden="true"
                    />
                  ) : (
                    <ChevronDown
                      size={16}
                      className="ml-auto flex-none text-muted-600"
                      aria-hidden="true"
                    />
                  )}
                </div>
                <div className="flex items-center gap-2.5 pl-4.5 text-helper text-muted-700">
                  <span>{day.items.length} stops</span>
                  <span className="text-muted-400">·</span>
                  <span>{day.route_optimization.local_distance_km} km</span>
                  <span className="text-muted-400">·</span>
                  <span className="font-semibold text-ink">
                    {formatMoney(daySpend(day))}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-0.5 pl-4.5">
                  {day.items.map((item, index) => (
                    <span
                      key={item.candidate_id}
                      className="flex items-center gap-1.5 rounded-pill border border-border bg-surface py-[5px] pr-2.5 pl-1.5 text-helper"
                    >
                      <span className="flex h-4 w-4 items-center justify-center rounded-full bg-accent-100 text-[10px] font-semibold text-accent-700">
                        {index + 1}
                      </span>
                      {item.name}
                    </span>
                  ))}
                </div>
              </button>

              {open && (
                <div className="flex flex-col gap-2 border-t border-divider px-4.5 pt-1 pb-4.5">
                  {day.items.map((item, index) => {
                    const leg = day.legs[index];
                    const tag = CATEGORY_TAGS[item.category];
                    return (
                      <div key={item.candidate_id} className="flex flex-col">
                        <TimelineRow>
                          <span className="flex h-5.5 w-5.5 flex-none items-center justify-center rounded-full bg-accent text-[11px] font-semibold text-white">
                            {index + 1}
                          </span>
                          <div className="mt-2 flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border bg-surface px-3.5 py-3">
                            <span className="flex-none font-mono text-[12px] text-accent-700">
                              {item.start_time}–{item.end_time}
                            </span>
                            <span className="min-w-0 flex-1 text-sm font-medium">
                              {item.name}
                            </span>
                            {tag && (
                              <PillTag tone={tag.tone}>{tag.label}</PillTag>
                            )}
                            <span className="min-w-14 flex-none text-right text-helper text-muted-700">
                              {formatMoney(item.cost)}
                            </span>
                          </div>
                        </TimelineRow>
                        {leg && (
                          <TimelineRow>
                            <span />
                            <div className="mt-2 flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-dashed border-muted-300 px-3.5 py-2.5">
                              <span className="flex-none font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
                                {leg.mode}
                              </span>
                              <span className="text-helper text-muted-700">
                                {leg.duration_minutes} min ·{" "}
                                {formatMoney(leg.cost)}
                              </span>
                            </div>
                          </TimelineRow>
                        )}
                      </div>
                    );
                  })}
                  {/* Display-only for now, like the chat stop chips: these need
                      the backend to support editing a single day. */}
                  <div className="flex gap-2 pt-1 pl-9.5">
                    <button
                      type="button"
                      className="rounded-pill border border-border bg-surface px-3.25 py-1.75 text-[13px] font-medium text-ink shadow-control"
                    >
                      Add a stop
                    </button>
                    <button
                      type="button"
                      className="rounded-pill px-3.25 py-1.75 text-[13px] font-medium text-muted-700"
                    >
                      Regenerate this day
                    </button>
                  </div>
                </div>
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}

function TimelineRow({ children }) {
  const [marker, body] = children;
  return (
    <div className="flex items-stretch gap-3">
      <div className="flex w-6.5 flex-none flex-col items-center pt-3.5">
        {marker}
        <span className="w-px flex-1 bg-border" />
      </div>
      {body}
    </div>
  );
}

function ComingSoon({ tab }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-1.5 rounded-xl bg-inset px-6 py-16 text-center">
      <span className="font-heading text-md font-semibold">
        {tab} is coming soon
      </span>
      <span className="text-body-sm text-muted-600">
        This tab isn&apos;t built yet. Summary and Itinerary are ready to
        explore.
      </span>
    </div>
  );
}

function TabsPanel() {
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
        {tab === "Itinerary" && <ItineraryTab />}
        {(tab === "Map" || tab === "Budget") && <ComingSoon tab={tab} />}
      </div>
    </section>
  );
}

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

      <main className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] grid-rows-[minmax(0,1fr)] gap-3.5 px-6 pb-6">
        <section
          aria-label="Trip planning chat"
          className="flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-surface shadow-control"
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

        <TabsPanel />
      </main>
    </div>
  );
}

export default TripPlanChatPage;
