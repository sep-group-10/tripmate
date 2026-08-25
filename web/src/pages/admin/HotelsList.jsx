import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import hotels from "../../services/hotelsData";

const DESTINATION_OPTIONS = [
  "All",
  ...new Set(hotels.map((h) => h.destination)),
];
const TIER_OPTIONS = ["All", ...new Set(hotels.map((h) => h.tier))];

function HotelsList() {
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [tierFilter, setTierFilter] = useState("All");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return hotels
      .filter(
        (h) =>
          destinationFilter === "All" || h.destination === destinationFilter,
      )
      .filter((h) => tierFilter === "All" || h.tier === tierFilter)
      .filter(
        (h) =>
          !q ||
          h.name.toLowerCase().includes(q) ||
          h.description.toLowerCase().includes(q),
      );
  }, [query, destinationFilter, tierFilter]);

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-[11px] font-medium tracking-widest text-muted-600 uppercase">
          Admin · Hotels
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-[28px] font-semibold tracking-tight">
          Hotels
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search hotels…"
          className="w-[260px]"
        />
        <select
          value={destinationFilter}
          onChange={(event) => setDestinationFilter(event.target.value)}
          aria-label="Destination"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          {DESTINATION_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option === "All" ? "All destinations" : option}
            </option>
          ))}
        </select>
        <select
          value={tierFilter}
          onChange={(event) => setTierFilter(event.target.value)}
          aria-label="Tier"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          {TIER_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option === "All" ? "All tiers" : option}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((hotel) => (
          <EntityCard
            key={hotel.id}
            name={hotel.name}
            location={hotel.destination}
            rating={hotel.rating}
            tag={{ label: hotel.tier, tone: "warn" }}
            description={hotel.description}
            metrics={[{ label: "Price / night", value: hotel.pricePerNight }]}
            chips={hotel.facilities}
          />
        ))}
      </div>
    </div>
  );
}

export default HotelsList;
