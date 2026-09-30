import { MapPin } from "lucide-react";
import { ITINERARY_DAYS, ROUTE_LEGS } from "../../data/tripPlanDummyData";
import { formatDate, formatDuration } from "../../utils/tripFormat";

const DAY_COLORS = ["bg-accent", "bg-info", "bg-muted-500"];

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

export default MapTab;
