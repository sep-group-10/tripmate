import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";

const CUISINE_TONES = {
  "Sri Lankan": "warn",
  Seafood: "info",
  International: "accent",
  "Street Food": "success",
};

const CUISINE_OPTIONS = Object.keys(CUISINE_TONES);

function RestaurantsList() {
  const {
    restaurants,
    destinations,
    addRestaurant,
    updateRestaurant,
    deleteRestaurant,
  } = useTourismData();
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [cuisineFilter, setCuisineFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [deletingRecord, setDeletingRecord] = useState(null);

  const destinationNames = useMemo(
    () => destinations.map((d) => d.name),
    [destinations],
  );

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
  }, [restaurants, query, destinationFilter, cuisineFilter]);

  const formFields = useMemo(
    () => [
      {
        name: "name",
        label: "Restaurant name",
        type: "text",
        placeholder: "e.g. Ministry of Crab",
        required: true,
      },
      {
        name: "destination",
        label: "Destination",
        type: "select",
        options: destinationNames,
        required: true,
      },
      {
        name: "cuisine",
        label: "Cuisine",
        type: "select",
        options: CUISINE_OPTIONS,
        required: true,
      },
      {
        name: "description",
        label: "Description",
        type: "textarea",
        placeholder: "Brief description shown to travellers…",
        required: true,
      },
      {
        name: "hours",
        label: "Hours",
        type: "text",
        placeholder: "e.g. 11:30–23:00",
      },
      {
        name: "priceRange",
        label: "Price range",
        type: "text",
        placeholder: "e.g. LKR 2,000–5,000",
      },
    ],
    [destinationNames],
  );

  const openAddForm = () => {
    setEditingRecord(null);
    setIsFormOpen(true);
  };

  const openEditForm = (record) => {
    setEditingRecord(record);
    setIsFormOpen(true);
  };

  const handleSubmit = (values) => {
    if (editingRecord) {
      updateRestaurant(editingRecord.id, values);
    } else {
      addRestaurant(values);
    }
    setIsFormOpen(false);
  };

  const handleConfirmDelete = () => {
    deleteRestaurant(deletingRecord.id);
    setDeletingRecord(null);
  };

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
          <option value="All">All destinations</option>
          {destinationNames.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <select
          value={cuisineFilter}
          onChange={(event) => setCuisineFilter(event.target.value)}
          aria-label="Cuisine"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          <option value="All">All cuisines</option>
          {CUISINE_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={openAddForm}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
        >
          ＋ Add Restaurant
        </button>
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
            onEdit={() => openEditForm(restaurant)}
            onDelete={() => setDeletingRecord(restaurant)}
          />
        ))}
      </div>

      {isFormOpen && (
        <EntityFormModal
          title={editingRecord ? "Edit Restaurant" : "Add Restaurant"}
          subtitle={
            editingRecord
              ? "Update this restaurant's details."
              : "Add a new restaurant to the destination database."
          }
          submitLabel={editingRecord ? "Save changes" : "Save Restaurant"}
          fields={formFields}
          initialValues={editingRecord}
          onSubmit={handleSubmit}
          onClose={() => setIsFormOpen(false)}
        />
      )}

      {deletingRecord && (
        <ConfirmDeleteDialog
          recordName={deletingRecord.name}
          onConfirm={handleConfirmDelete}
          onClose={() => setDeletingRecord(null)}
        />
      )}
    </div>
  );
}

export default RestaurantsList;
