// Trip-plan page, still on dummy data with no real API. Chat panel on the left,
// tabs panel on the right (Summary + Itinerary built; Map and Budget are
// placeholders). Session list and mobile layout come in later steps.
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronUp, MapPin, SendHorizontal } from "lucide-react";

const SUGGESTIONS = ["Swap a day", "Cut LKR 10,000", "Add a tea estate visit"];

const REPLY_DELAY_MS = 1000;

// Dummy itinerary, shaped like ChatItineraryDay / ChatItineraryItem
// (backend/app/schemas/chat.py): day_number, date, items[] with candidate_id,
// category, name, start_time, end_time, and route_optimization.local_distance_km.
// The real schema has NO costs, travel legs or day titles yet, so `cost` (LKR,
// for both travellers), `legs` (one per gap between items; `intercity` marks the
// long drive) and `title` below are dummy-only extras that the backend would need
// to add before this can be wired to a ChatResponse. Place names come from the
// seeded Kandy data; Ella has no seeded places yet.
const ITINERARY_DAYS = [
  {
    day_number: 1,
    date: "2026-10-12",
    title: "Kandy heritage & lake",
    route_optimization: { local_distance_km: 4.1 },
    hotel_id: "hotel-kandy",
    items: [
      {
        candidate_id: "attr-1",
        category: "attraction",
        name: "Temple of the Sacred Tooth Relic",
        start_time: "09:00",
        end_time: "11:00",
        cost: 4000,
      },
      {
        candidate_id: "rest-1",
        category: "restaurant",
        name: "Lunch at Kandy Spice Garden",
        start_time: "12:00",
        end_time: "13:15",
        cost: 3600,
      },
      {
        candidate_id: "attr-2",
        category: "attraction",
        name: "Kandy Lake",
        start_time: "14:00",
        end_time: "15:30",
        cost: 0,
      },
    ],
    legs: [
      { mode: "Tuk-tuk", duration_minutes: 10, cost: 600 },
      { mode: "Tuk-tuk", duration_minutes: 8, cost: 500 },
    ],
  },
  {
    day_number: 2,
    date: "2026-10-13",
    title: "Kandy to Ella",
    route_optimization: { local_distance_km: 9.4 },
    hotel_id: "hotel-ella",
    items: [
      {
        candidate_id: "attr-3",
        category: "attraction",
        name: "Royal Botanical Gardens",
        start_time: "08:00",
        end_time: "10:00",
        cost: 6000,
      },
      {
        candidate_id: "attr-4",
        category: "attraction",
        name: "Nine Arch Bridge",
        start_time: "15:00",
        end_time: "16:00",
        cost: 0,
      },
      {
        candidate_id: "rest-2",
        category: "restaurant",
        name: "Dinner in Ella town",
        start_time: "19:00",
        end_time: "20:30",
        cost: 5000,
      },
    ],
    legs: [
      { mode: "Car", duration_minutes: 255, cost: 24000, intercity: true },
      { mode: "Tuk-tuk", duration_minutes: 12, cost: 1200 },
    ],
  },
  {
    day_number: 3,
    date: "2026-10-14",
    title: "Ella viewpoints",
    route_optimization: { local_distance_km: 14.8 },
    hotel_id: null, // departure day: no overnight stay
    items: [
      {
        candidate_id: "attr-5",
        category: "attraction",
        name: "Ella Rock",
        start_time: "06:30",
        end_time: "10:30",
        cost: 3000,
      },
      {
        candidate_id: "rest-3",
        category: "restaurant",
        name: "Lunch in Ella town",
        start_time: "12:00",
        end_time: "13:15",
        cost: 4500,
      },
      {
        candidate_id: "attr-6",
        category: "attraction",
        name: "Little Adam's Peak",
        start_time: "15:30",
        end_time: "17:30",
        cost: 0,
      },
    ],
    legs: [
      { mode: "Tuk-tuk", duration_minutes: 15, cost: 1200 },
      { mode: "Tuk-tuk", duration_minutes: 10, cost: 800 },
    ],
  },
];

// Hotel data as cost_estimator.py sees it: each day carries the hotel_id of the
// night it ends with, the itinerary maps destination -> hotel_id
// (hotel_by_destination), and the nightly price lives on the hotel candidate,
// which is stood in for by HOTELS here. ChatItineraryDay's hotel_location is
// left out because nothing on this page draws it yet. 3 days = 2 nights.
const HOTEL_BY_DESTINATION = { Kandy: "hotel-kandy", Ella: "hotel-ella" };

const HOTELS = {
  "hotel-kandy": { name: "Hill View Kandy", price_per_night: 14000 },
  "hotel-ella": { name: "Ella guesthouse", price_per_night: 12000 },
};

// Same rate as _MISC_RATE in cost_estimator.py.
const MISC_RATE = 0.1;

const TRIP_FACTS = {
  title: "Three days from Kandy to Ella",
  places: "Kandy · Ella",
  travellers: "2 adults",
  pace: "Relaxed",
};

const TRADEOFFS = [
  {
    tag: "Swapped",
    tone: "info",
    text: "The Royal Botanical Gardens moved to Day 2 morning — it sits on the road out of Kandy, so it fills the time before the long drive to Ella without backtracking.",
  },
  {
    tag: "Kept",
    tone: "success",
    text: "The private car for Kandy to Ella stayed despite the cost: the drive is about four hours, while the scenic train is closer to seven.",
  },
  {
    tag: "Dropped",
    tone: "warn",
    text: "Sigiriya — it's a long detour from Kandy and doesn't fit a relaxed pace with two travellers on a three-day trip.",
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

// Dummy route legs, consistent with the day data above (Kandy to Ella is about
// 137 km and roughly four hours by road).
const ROUTE_LEGS = [
  {
    label: "Leg 1",
    text: "Day 1 → Day 2 · Kandy Lake → Royal Botanical Gardens, by tuk-tuk",
    distance_km: 6.2,
    duration_minutes: 20,
  },
  {
    label: "Leg 2",
    text: "Day 2 · Royal Botanical Gardens → Nine Arch Bridge, Kandy to Ella by car",
    distance_km: 137,
    duration_minutes: 255,
  },
  {
    label: "Leg 3",
    text: "Day 2 → Day 3 · Nine Arch Bridge → Ella Rock trailhead, by tuk-tuk",
    distance_km: 4.8,
    duration_minutes: 15,
  },
];

const DAY_COLORS = ["bg-accent", "bg-info", "bg-muted-500"];

// Category keys mirror cost_estimator.py's output. Each maps from an itinerary
// item category (legs map to local or intercity transport), so the breakdown is
// derived from ITINERARY_DAYS and always adds up to the Itinerary tab's total.
const BUDGET_CATEGORIES = [
  { key: "accommodation", label: "Accommodation", color: "bg-accent" },
  { key: "dining", label: "Dining", color: "bg-info" },
  {
    key: "transport_intercity",
    label: "Intercity transport",
    color: "bg-success",
  },
  { key: "transport_local", label: "Local transport", color: "bg-warn" },
  { key: "activities", label: "Activities", color: "bg-accent-300" },
  { key: "miscellaneous", label: "Miscellaneous", color: "bg-muted-400" },
];

const ITEM_BUDGET_KEYS = {
  hotel: "accommodation",
  restaurant: "dining",
  attraction: "activities",
};

// Dummy content is shaped loosely like ChatItineraryDay / ChatItineraryItem
// (backend/app/schemas/chat.py) so it can be swapped for a real ChatResponse.
// `stops` are place names (in a real response, itinerary items[].name) and
// `actions` are short follow-up prompts shown under an assistant message.
const INITIAL_MESSAGES = [
  {
    id: "m1",
    role: "assistant",
    text: "Hi! Tell me where you'd like to go, for how long and what you enjoy, and I'll sketch a plan. Here's a sample of what a day can look like:",
    stops: ["Sacred Tooth Relic", "Kandy Spice Garden", "Kandy Lake"],
    actions: ["Make it cheaper", "Add a rest day", "Regenerate Day 1"],
    itineraryDay: ITINERARY_DAYS[0],
  },
  {
    id: "m2",
    role: "user",
    text: "Plan 3 days in Kandy and Ella for two, we love food and walking.",
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
  return amount === 0 ? freeLabel : `LKR ${amount.toLocaleString("en-US")}`;
}

function formatDuration(minutes) {
  if (minutes < 60) return `${minutes} min`;
  const rest = minutes % 60;
  return `${Math.floor(minutes / 60)} h${rest ? ` ${rest} min` : ""}`;
}

function dayHotel(day) {
  return day.hotel_id ? HOTELS[day.hotel_id] : null;
}

// One night per day that has a hotel_id, priced per night, like
// _accommodation_cost in cost_estimator.py.
function daySpend(day) {
  const hotel = dayHotel(day);
  return (
    [...day.items, ...day.legs].reduce((sum, row) => sum + row.cost, 0) +
    (hotel ? hotel.price_per_night : 0)
  );
}

// Shared by the Itinerary and Budget tabs so their totals always agree.
// Miscellaneous is MISC_RATE of the other categories' subtotal, as in
// cost_estimator.py. The real values exist there but aren't exposed on
// ChatResponse yet (and there they are min/max ranges, not single numbers).
function computeBudget() {
  const amounts = Object.fromEntries(
    BUDGET_CATEGORIES.map(({ key }) => [key, 0]),
  );
  ITINERARY_DAYS.forEach((day) => {
    day.items.forEach((item) => {
      amounts[ITEM_BUDGET_KEYS[item.category]] += item.cost;
    });
    day.legs.forEach((leg) => {
      amounts[leg.intercity ? "transport_intercity" : "transport_local"] +=
        leg.cost;
    });
  });
  // Nights per hotel = days sharing its hotel_id, like _nights_per_destination.
  amounts.accommodation = Object.values(HOTEL_BY_DESTINATION).reduce(
    (sum, hotelId) =>
      sum +
      HOTELS[hotelId].price_per_night *
        ITINERARY_DAYS.filter((day) => day.hotel_id === hotelId).length,
    0,
  );
  const subtotal = Object.values(amounts).reduce((sum, n) => sum + n, 0);
  amounts.miscellaneous = Math.round(subtotal * MISC_RATE);
  return { amounts, total: subtotal + amounts.miscellaneous };
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
          Your plan keeps Day 1 walkable around Kandy — the Temple of the Sacred
          Tooth Relic, a local lunch and Kandy Lake sit within a few kilometres
          of each other. The long drive to Ella is on Day 2 with only light
          stops around it, and Day 3 is saved for Ella&apos;s two viewpoints so
          both land in clear morning and late-afternoon light.
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
  const totalSpend = computeBudget().total;

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
                            <span className="min-w-16 flex-none text-right text-helper text-muted-700">
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
                                {formatDuration(leg.duration_minutes)} ·{" "}
                                {formatMoney(leg.cost)}
                              </span>
                            </div>
                          </TimelineRow>
                        )}
                      </div>
                    );
                  })}
                  {dayHotel(day) && (
                    <TimelineRow>
                      <span />
                      <div className="mt-2 flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-dashed border-muted-300 px-3.5 py-2.5">
                        <span className="flex-none font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
                          Stay
                        </span>
                        <span className="min-w-0 flex-1 text-helper text-muted-700">
                          Overnight at {dayHotel(day).name}
                        </span>
                        <span className="flex-none text-helper text-muted-700">
                          {formatMoney(dayHotel(day).price_per_night)}
                        </span>
                      </div>
                    </TimelineRow>
                  )}
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

function MapTab() {
  return (
    <>
      {/* Placeholder on purpose: the backend has lat/lng per item but no
          leg-by-leg route data yet (only route_optimization.local_distance_km
          per day), so there is nothing real to draw a route from. */}
      <div className="flex min-h-64 flex-none flex-col items-center justify-center gap-2 rounded-[14px] border border-border bg-inset px-6 text-center">
        <MapPin size={22} className="text-muted-500" aria-hidden="true" />
        <span className="font-heading text-md font-semibold">Route map</span>
        <span className="max-w-[36ch] text-body-sm text-muted-600">
          Coming once real trip data is wired up. Stops and legs will be drawn
          here.
        </span>
      </div>

      <div className="flex flex-none flex-wrap gap-2">
        {ITINERARY_DAYS.map((day, index) => (
          <span
            key={day.day_number}
            className="flex items-center gap-2 rounded-pill border border-border px-3 py-1.5 text-helper"
          >
            <span className={`h-2 w-2 rounded-full ${DAY_COLORS[index]}`} />
            Day {day.day_number} · {formatDate(day.date)}
          </span>
        ))}
      </div>

      <div className="flex flex-none flex-col">
        {ROUTE_LEGS.map((leg) => (
          <div
            key={leg.label}
            className="flex items-baseline gap-3 border-t border-divider py-2.5"
          >
            <span className="w-11.5 flex-none font-mono text-badge font-medium tracking-wider text-accent-700 uppercase">
              {leg.label}
            </span>
            <span className="flex-1 text-body-sm text-muted-700">
              {leg.text}
            </span>
            <span className="text-helper text-muted-500">
              {leg.distance_km} km · {formatDuration(leg.duration_minutes)}
            </span>
          </div>
        ))}
      </div>
    </>
  );
}

function BudgetTab() {
  const { amounts, total } = computeBudget();
  const rows = BUDGET_CATEGORIES.map((category) => ({
    ...category,
    amount: amounts[category.key],
    percent: total ? Math.round((amounts[category.key] / total) * 100) : 0,
  }));

  return (
    <>
      <div className="flex flex-none items-baseline justify-between gap-3">
        <SectionLabel>Total planned spend</SectionLabel>
        <span className="flex items-baseline gap-2">
          <span className="font-heading text-[26px] font-semibold tracking-tight text-accent">
            {formatMoney(total)}
          </span>
          <span className="text-helper text-muted-500">
            {formatMoney(Math.round(total / ITINERARY_DAYS.length))} / day
          </span>
        </span>
      </div>

      <div
        className="flex h-2.5 flex-none overflow-hidden rounded-pill bg-inset"
        role="img"
        aria-label="Spend by category"
      >
        {rows
          .filter((row) => row.amount > 0)
          .map((row) => (
            <span
              key={row.key}
              className={`h-full ${row.color}`}
              style={{ width: `${row.percent}%` }}
            />
          ))}
      </div>

      <div className="flex flex-none flex-col">
        {rows.map((row) => (
          <div
            key={row.key}
            className="flex items-center gap-2.5 border-t border-divider py-2.75"
          >
            <span className={`h-2 w-2 flex-none rounded-full ${row.color}`} />
            <span className="flex-1 text-body-sm text-muted-700">
              {row.label}
            </span>
            <span className="text-helper text-muted-500">
              {row.amount > 0 ? `${row.percent}%` : "—"}
            </span>
            <span
              className={`min-w-22 text-right text-body-sm font-medium ${row.amount > 0 ? "" : "text-muted-500"}`}
            >
              {formatMoney(row.amount, "LKR 0")}
            </span>
          </div>
        ))}
      </div>
    </>
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
        {tab === "Map" && <MapTab />}
        {tab === "Budget" && <BudgetTab />}
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
  // Planning-session id. Nothing sets it from a real reply yet; it will be set
  // from ChatResponse.session.id on the first real reply, then sent back so
  // later messages continue the same session.
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const mounted = useRef(true);
  const replyCount = useRef(0);
  const listEndRef = useRef(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  // Lets an in-flight reply be dropped if the page unmounts before it lands.
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const canSend = input.trim().length > 0 && !thinking;

  // AI INTEGRATION POINT. Replace this function's body with a real POST to
  // /api/v1/chat (or /api/v1/chat/{session_id} for a continuing session) once
  // the backend planner is ready. See backend/app/schemas/chat.py for the real
  // ChatResponse shape this page's message data already mirrors. It should
  // resolve with a ChatResponse ({ assistant_message, session, itinerary })
  // and reject on failure. The dummy ignores both arguments.
  // eslint-disable-next-line no-unused-vars
  const requestAssistantReply = (text, currentSessionId) =>
    new Promise((resolve) => {
      setTimeout(() => {
        const reply = DUMMY_REPLIES[replyCount.current % DUMMY_REPLIES.length];
        replyCount.current += 1;
        resolve({ assistant_message: reply, session: null, itinerary: null });
      }, REPLY_DELAY_MS);
    });

  const handleSend = async (event) => {
    event.preventDefault();
    if (!canSend) return;

    const text = input.trim();
    setMessages((prev) => [
      ...prev,
      { id: `u-${Date.now()}`, role: "user", text },
    ]);
    setInput("");
    setError(null);
    setThinking(true);

    try {
      const response = await requestAssistantReply(text, sessionId);
      if (!mounted.current) return;
      if (response.session?.id) setSessionId(response.session.id);
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          text: response.assistant_message,
        },
      ]);
    } catch {
      // Unreachable today (the dummy never rejects); this is where a failed
      // real call lands so the thinking indicator can't get stuck.
      if (!mounted.current) return;
      setError("Something went wrong — try again");
    } finally {
      if (mounted.current) setThinking(false);
    }
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
            {error && (
              <p role="alert" className="m-0 text-body-sm text-danger">
                {error}
              </p>
            )}
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
