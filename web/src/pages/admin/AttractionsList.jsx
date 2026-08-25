import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import attractions from "../../services/attractionsData";

const CATEGORY_TONES = {
  Historical: "warn",
  Hiking: "success",
  Nature: "info",
  Religious: "accent",
};

const DESTINATION_OPTIONS = [
  "All",
  ...new Set(attractions.map((a) => a.destination)),
];
const CATEGORY_OPTIONS = [
  "All",
  ...new Set(attractions.map((a) => a.category)),
];

function AttractionsList() {
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [categoryFilter, setCategoryFilter] = useState("All");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return attractions
      .filter(
        (a) =>
          destinationFilter === "All" || a.destination === destinationFilter,
      )
      .filter((a) => categoryFilter === "All" || a.category === categoryFilter)
      .filter(
        (a) =>
          !q ||
          a.name.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q),
      );
  }, [query, destinationFilter, categoryFilter]);

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-[11px] font-medium tracking-widest text-muted-600 uppercase">
          Admin · Attractions
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-[28px] font-semibold tracking-tight">
          Attractions
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search attractions…"
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
          value={categoryFilter}
          onChange={(event) => setCategoryFilter(event.target.value)}
          aria-label="Category"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          {CATEGORY_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option === "All" ? "All categories" : option}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((attraction) => (
          <EntityCard
            key={attraction.id}
            name={attraction.name}
            location={attraction.destination}
            rating={attraction.rating}
            tag={{
              label: attraction.category,
              tone: CATEGORY_TONES[attraction.category] || "accent",
            }}
            description={attraction.description}
            metrics={[
              { label: "Hours", value: attraction.hours },
              { label: "Entry", value: attraction.entry },
              { label: "Duration", value: attraction.duration },
            ]}
          />
        ))}
      </div>
    </div>
  );
}

export default AttractionsList;
