import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { ITINERARY_DAYS } from "../../data/tripPlanDummyData";
import { computeBudget, dayHotel, daySpend } from "../../utils/tripBudget";
import {
  formatDate,
  formatDuration,
  formatMoney,
} from "../../utils/tripFormat";
import PillTag from "./PillTag";

const CATEGORY_TAGS = {
  attraction: { label: "Attraction", tone: "info" },
  restaurant: { label: "Dining", tone: "warn" },
  hotel: { label: "Stay", tone: "outline" },
};

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

export default ItineraryTab;
