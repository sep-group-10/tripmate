import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import restaurants from "../../services/restaurantsData";

const CUISINE_TONES = {
  "Sri Lankan": "warn",
  Seafood: "info",
  International: "accent",
  "Street Food": "success",
};

const DESTINATION_OPTIONS = [
  "All",
  ...new Set(restaurants.map((r) => r.destination)),
];
const CUISINE_OPTIONS = ["All", ...new Set(restaurants.map((r) => r.cuisine))];

function RestaurantsList() {
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [cuisineFilter, setCuisineFilter] = useState("All");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return restaurants
      .filter(
        (r) =>
          destinationFilter === "All" || r.destination === destinationFilter,
      )
      .filter((r) => cuisineFilter === "All" || r.cuisine === cuisineFilter)
      .filter(
        (r) =>
          !q ||
          r.name.toLowerCase().includes(q) ||
          r.description.toLowerCase().includes(q),
      );
  }, [query, destinationFilter, cuisineFilter]);

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-[11px] font-medium tracking-widest text-muted-600 uppercase">
          Admin · Restaurants
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-[28px] font-semibold tracking-tight">
          Restaurants
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search restaurants…"
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
          value={cuisineFilter}
          onChange={(event) => setCuisineFilter(event.target.value)}
          aria-label="Cuisine"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          {CUISINE_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option === "All" ? "All cuisines" : option}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((restaurant) => (
          <EntityCard
            key={restaurant.id}
            name={restaurant.name}
            location={restaurant.destination}
            rating={restaurant.rating}
            tag={{
              label: restaurant.cuisine,
              tone: CUISINE_TONES[restaurant.cuisine] || "accent",
            }}
            description={restaurant.description}
            metrics={[
              { label: "Hours", value: restaurant.hours },
              { label: "Price range", value: restaurant.priceRange },
            ]}
          />
        ))}
      </div>
    </div>
  );
}

export default RestaurantsList;
