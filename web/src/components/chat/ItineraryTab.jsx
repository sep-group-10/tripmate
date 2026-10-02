import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { formatDate } from "../../utils/tripFormat";
import EmptyState from "./EmptyState";
import { TAB_EMPTY_STATES } from "./tabEmptyStates";
import PillTag from "./PillTag";
import SectionLabel from "./SectionLabel";

const CATEGORY_TAGS = {
  attraction: { label: "Attraction", tone: "info" },
  restaurant: { label: "Dining", tone: "warn" },
  hotel: { label: "Stay", tone: "outline" },
  local_event: { label: "Event", tone: "accent" },
};

function humanize(value) {
  return String(value)
    .replace(/_/g, " ")
    .replace(/^./, (char) => char.toUpperCase());
}

function categoryTag(category) {
  return (
    CATEGORY_TAGS[category] || {
      label: category ? humanize(category) : "Stop",
      tone: "outline",
    }
  );
}

// Renders a ChatItinerary (backend/app/schemas/chat.py). The real response has
// no costs, travel legs, day titles or hotel names, so none are shown; every
// field read here is either required by the schema or guarded.
function ItineraryTab({ itinerary }) {
  // null means "not chosen yet": default to the first day. 0 means "closed".
  const [activeDay, setActiveDay] = useState(null);
  const [openDay, setOpenDay] = useState(null);

  const days = itinerary?.days ?? [];
  if (days.length === 0) return <EmptyState {...TAB_EMPTY_STATES.Itinerary} />;

  const itemsOf = (day) => day.items ?? [];
  const firstDay = days[0].day_number;
  const currentDay = activeDay ?? firstDay;
  const expandedDay = openDay ?? firstDay;
  const stopCount = days.reduce((n, day) => n + itemsOf(day).length, 0);
  const unscheduled = itinerary.unscheduled ?? [];
  const warnings = itinerary.warnings ?? [];

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
    setOpenDay(expandedDay === dayNumber ? 0 : dayNumber);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end gap-4">
        <div className="flex min-w-0 flex-1 flex-col gap-0.5">
          <h2 className="font-heading m-0 text-[19px] font-semibold tracking-tight">
            {days.length}-day itinerary
          </h2>
          <span className="text-helper text-muted-600">
            {days.length > 1
              ? `${formatDate(days[0].date)} – ${formatDate(days.at(-1).date)}`
              : formatDate(days[0].date)}
          </span>
        </div>
        <span className="text-helper text-muted-600">{stopCount} stops</span>
      </div>

      <div className="flex gap-0.5 overflow-x-auto py-0.5">
        {days.map((day) => {
          const on = currentDay === day.day_number;
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
        {days.map((day) => {
          const open = expandedDay === day.day_number;
          const items = itemsOf(day);
          const distance = day.route_optimization?.local_distance_km;
          return (
            <section
              key={day.day_number}
              id={`itinerary-day-${day.day_number}`}
              className={`overflow-hidden rounded-panel border ${
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
                    {formatDate(day.date)}
                    {day.day_type ? ` · ${humanize(day.day_type)}` : ""}
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
                  <span>{items.length} stops</span>
                  {typeof distance === "number" && (
                    <>
                      <span className="text-muted-400">·</span>
                      <span>{Number(distance.toFixed(1))} km</span>
                    </>
                  )}
                </div>
                {items.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-0.5 pl-4.5">
                    {items.map((item, index) => (
                      <span
                        key={`${item.candidate_id}-${index}`}
                        className="flex items-center gap-1.5 rounded-pill border border-border bg-surface py-[5px] pr-2.5 pl-1.5 text-helper"
                      >
                        <span className="flex h-4 w-4 items-center justify-center rounded-full bg-accent-100 text-[10px] font-semibold text-accent-700">
                          {index + 1}
                        </span>
                        {item.name}
                      </span>
                    ))}
                  </div>
                )}
              </button>

              {open && (
                <div className="flex flex-col gap-2 border-t border-divider px-4.5 pt-1 pb-4.5">
                  {items.map((item, index) => {
                    const tag = categoryTag(item.category);
                    return (
                      <TimelineRow
                        key={`${item.candidate_id}-${index}`}
                        isLast={index === items.length - 1}
                      >
                        <span className="flex h-5.5 w-5.5 flex-none items-center justify-center rounded-full bg-accent text-[11px] font-semibold text-white">
                          {index + 1}
                        </span>
                        <div className="mt-2 flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border bg-surface px-3.5 py-3">
                          {item.start_time && (
                            <span className="flex-none font-mono text-[12px] text-accent-700">
                              {item.start_time}
                              {item.end_time ? `–${item.end_time}` : ""}
                            </span>
                          )}
                          <span className="min-w-0 flex-1 text-sm font-medium">
                            {item.name}
                          </span>
                          <PillTag tone={tag.tone}>{tag.label}</PillTag>
                        </div>
                      </TimelineRow>
                    );
                  })}
                  {(day.warnings ?? []).map((warning) => (
                    <p
                      key={warning}
                      className="m-0 pl-9.5 text-helper text-warn"
                    >
                      {warning}
                    </p>
                  ))}
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

      {unscheduled.length > 0 && (
        <div className="flex flex-col gap-2 rounded-xl bg-inset p-4">
          <SectionLabel>Couldn&apos;t fit in</SectionLabel>
          {unscheduled.map((item, index) => (
            <p
              key={`${item.candidate_id}-${index}`}
              className="m-0 text-body-sm text-muted-700"
            >
              <span className="font-medium text-ink">{item.name}</span>
              {item.reason ? ` — ${item.reason}` : ""}
            </p>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="flex flex-col gap-2 rounded-xl bg-inset p-4">
          <SectionLabel>Heads up</SectionLabel>
          {warnings.map((warning) => (
            <p key={warning} className="m-0 text-body-sm text-warn">
              {warning}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

function TimelineRow({ children, isLast }) {
  const [marker, body] = children;
  return (
    <div className="flex items-stretch gap-3">
      <div className="flex w-6.5 flex-none flex-col items-center pt-3.5">
        {marker}
        {!isLast && <span className="w-px flex-1 bg-border" />}
      </div>
      {body}
    </div>
  );
}

export default ItineraryTab;
