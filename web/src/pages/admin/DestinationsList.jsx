import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import destinations from "../../services/destinationsData";

const REGION_TONES = {
  "Hill Country": "success",
  "Cultural Triangle": "warn",
  Coastal: "info",
  Wildlife: "accent",
};

const REGION_OPTIONS = ["All", ...new Set(destinations.map((d) => d.tag))];

function DestinationsList() {
  const [query, setQuery] = useState("");
  const [regionFilter, setRegionFilter] = useState("All");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return destinations
      .filter((d) => regionFilter === "All" || d.tag === regionFilter)
      .filter(
        (d) =>
          !q ||
          d.name.toLowerCase().includes(q) ||
          d.description.toLowerCase().includes(q),
      );
  }, [query, regionFilter]);

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-[11px] font-medium tracking-widest text-muted-600 uppercase">
          Admin · Destinations
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-[28px] font-semibold tracking-tight">
          Destinations
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search destinations…"
          className="w-[260px]"
        />
        <select
          value={regionFilter}
          onChange={(event) => setRegionFilter(event.target.value)}
          aria-label="Region"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          {REGION_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option === "All" ? "All regions" : option}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((destination) => (
          <EntityCard
            key={destination.id}
            name={destination.name}
            location={`${destination.region}, ${destination.country}`}
            rating={destination.rating}
            tag={{
              label: destination.tag,
              tone: REGION_TONES[destination.tag] || "accent",
            }}
            description={destination.description}
            metrics={[
              { label: "Region", value: destination.region },
              { label: "Country", value: destination.country },
            ]}
          />
        ))}
      </div>
    </div>
  );
}

export default DestinationsList;
