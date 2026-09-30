import { MapPin } from "lucide-react";
import { formatDate } from "../../utils/tripFormat";
import EmptyState from "./EmptyState";

const DAY_COLORS = ["bg-accent", "bg-info", "bg-muted-500"];

function hasCoords(item) {
  return (
    typeof item.latitude === "number" && typeof item.longitude === "number"
  );
}

// Great-circle distance between two stops, in km.
function straightLineKm(a, b) {
  const toRad = (degrees) => (degrees * Math.PI) / 180;
  const dLat = toRad(b.latitude - a.latitude);
  const dLon = toRad(b.longitude - a.longitude);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a.latitude)) *
      Math.cos(toRad(b.latitude)) *
      Math.sin(dLon / 2) ** 2;
  return 2 * 6371 * Math.asin(Math.sqrt(h));
}

// Reads a ChatItinerary. The backend gives lat/lng per stop but no routed
// legs (only route_optimization.local_distance_km per day), so there is no
// route to draw: the map area stays a placeholder and the legs below are
// straight-line distances between consecutive stops, computed here.
function MapTab({ itinerary }) {
  const days = itinerary?.days ?? [];
  if (days.length === 0) return <EmptyState what="route map" />;

  const stops = days.flatMap((day) =>
    (day.items ?? [])
      .filter(hasCoords)
      .map((item) => ({ ...item, day_number: day.day_number })),
  );
  const legs = stops.slice(1).map((to, index) => {
    const from = stops[index];
    return { from, to, km: straightLineKm(from, to) };
  });

  return (
    <>
      <div className="flex min-h-64 flex-none flex-col items-center justify-center gap-2 rounded-[14px] border border-border bg-inset px-6 text-center">
        <MapPin size={22} className="text-muted-500" aria-hidden="true" />
        <span className="font-heading text-md font-semibold">Route map</span>
        <span className="max-w-[36ch] text-body-sm text-muted-600">
          The interactive map is coming soon. Your stops and the distances
          between them are listed below.
        </span>
      </div>

      <div className="flex flex-none flex-wrap gap-2">
        {days.map((day, index) => (
          <span
            key={day.day_number}
            className="flex items-center gap-2 rounded-pill border border-border px-3 py-1.5 text-helper"
          >
            <span
              className={`h-2 w-2 rounded-full ${DAY_COLORS[index % DAY_COLORS.length]}`}
            />
            Day {day.day_number} · {formatDate(day.date)}
          </span>
        ))}
      </div>

      <div className="flex flex-none flex-col">
        {legs.length === 0 ? (
          <p className="m-0 border-t border-divider pt-3 text-body-sm text-muted-600">
            Not enough stops with coordinates to show distances yet.
          </p>
        ) : (
          legs.map(({ from, to, km }, index) => (
            <div
              key={`${index}-${from.candidate_id}-${to.candidate_id}`}
              className="flex items-baseline gap-3 border-t border-divider py-2.5"
            >
              <span className="w-11.5 flex-none font-mono text-badge font-medium tracking-wider text-accent-700 uppercase">
                Leg {index + 1}
              </span>
              <span className="flex-1 text-body-sm text-muted-700">
                {from.day_number === to.day_number
                  ? `Day ${from.day_number}`
                  : `Day ${from.day_number} → Day ${to.day_number}`}{" "}
                · {from.name} → {to.name}
              </span>
              <span className="text-helper text-muted-500">
                ≈ {km.toFixed(1)} km
              </span>
            </div>
          ))
        )}
        {legs.length > 0 && (
          <p className="m-0 border-t border-divider pt-2.5 text-helper text-muted-500">
            Straight-line distances between consecutive stops, not road routes.
          </p>
        )}
      </div>
    </>
  );
}

export default MapTab;
