import { formatDate } from "../../utils/tripFormat";
import EmptyState from "./EmptyState";
import TripMap from "./TripMap";

// One entry per day, in order, reused when there are more days than colors.
// `dot` colors the legend and `hex` colors that day's pins, so they match.
const DAY_COLORS = [
  { dot: "bg-accent", hex: "#e8532b" },
  { dot: "bg-info", hex: "#2f6ff0" },
  { dot: "bg-muted-500", hex: "#9aa0a3" },
  { dot: "bg-success", hex: "#12a26a" },
  { dot: "bg-warn", hex: "#d68a00" },
];

// Coordinates may be missing (null) on some stops; coerce like LocationPicker
// does and treat anything that isn't a finite number as "no location".
function coordinate(value) {
  return value == null ? NaN : Number(value);
}

function hasCoords(item) {
  return (
    Number.isFinite(coordinate(item.latitude)) &&
    Number.isFinite(coordinate(item.longitude))
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

// Reads a ChatItinerary. The map pins every stop that has lat/lng, colored by
// day. The backend gives no routed legs (only
// route_optimization.local_distance_km per day), so no route line is drawn and
// the legs below are straight-line distances between consecutive stops,
// computed here.
function MapTab({ itinerary }) {
  const days = itinerary?.days ?? [];
  if (days.length === 0) return <EmptyState what="route map" />;

  // `number` is the stop's position in its day (counting stops with no
  // coordinates too) so pins match the numbering on the Itinerary tab.
  const stops = days.flatMap((day, dayIndex) =>
    (day.items ?? [])
      .map((item, index) => ({ item, number: index + 1 }))
      .filter(({ item }) => hasCoords(item))
      .map(({ item, number }) => ({
        ...item,
        latitude: coordinate(item.latitude),
        longitude: coordinate(item.longitude),
        day_number: day.day_number,
        dayIndex,
        number,
      })),
  );
  const pins = stops.map((stop, index) => ({
    key: `${index}-${stop.candidate_id}`,
    name: stop.name,
    lat: stop.latitude,
    lng: stop.longitude,
    number: stop.number,
    day_number: stop.day_number,
    start_time: stop.start_time,
    pinColor: DAY_COLORS[stop.dayIndex % DAY_COLORS.length].hex,
  }));
  const legs = stops.slice(1).map((to, index) => {
    const from = stops[index];
    return { from, to, km: straightLineKm(from, to) };
  });

  return (
    <>
      <TripMap stops={pins} />

      <div className="flex flex-none flex-wrap gap-2">
        {days.map((day, index) => (
          <span
            key={day.day_number}
            className="flex items-center gap-2 rounded-pill border border-border px-3 py-1.5 text-helper"
          >
            <span
              className={`h-2 w-2 rounded-full ${DAY_COLORS[index % DAY_COLORS.length].dot}`}
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
