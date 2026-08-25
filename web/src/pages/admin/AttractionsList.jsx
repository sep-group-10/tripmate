import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";

const CATEGORY_TONES = {
  Historical: "warn",
  Hiking: "success",
  Nature: "info",
  Religious: "accent",
};

const CATEGORY_OPTIONS = Object.keys(CATEGORY_TONES);

function AttractionsList() {
  const {
    attractions,
    destinations,
    addAttraction,
    updateAttraction,
    deleteAttraction,
  } = useTourismData();
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [deletingRecord, setDeletingRecord] = useState(null);

  const destinationNames = useMemo(
    () => destinations.map((d) => d.name),
    [destinations],
  );

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
  }, [attractions, query, destinationFilter, categoryFilter]);

  const formFields = useMemo(
    () => [
      {
        name: "name",
        label: "Attraction name",
        type: "text",
        placeholder: "e.g. Nine Arch Bridge",
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
        name: "category",
        label: "Category",
        type: "select",
        options: CATEGORY_OPTIONS,
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
        placeholder: "e.g. 6:00–18:00",
      },
      {
        name: "entry",
        label: "Entry fee",
        type: "text",
        placeholder: "e.g. LKR 500",
      },
      {
        name: "duration",
        label: "Duration",
        type: "text",
        placeholder: "e.g. 1–2 hr",
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
      updateAttraction(editingRecord.id, values);
    } else {
      addAttraction(values);
    }
    setIsFormOpen(false);
  };

  const handleConfirmDelete = () => {
    deleteAttraction(deletingRecord.id);
    setDeletingRecord(null);
  };

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
          <option value="All">All destinations</option>
          {destinationNames.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <select
          value={categoryFilter}
          onChange={(event) => setCategoryFilter(event.target.value)}
          aria-label="Category"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          <option value="All">All categories</option>
          {CATEGORY_OPTIONS.map((option) => (
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
          ＋ Add Attraction
        </button>
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
            onEdit={() => openEditForm(attraction)}
            onDelete={() => setDeletingRecord(attraction)}
          />
        ))}
      </div>

      {isFormOpen && (
        <EntityFormModal
          title={editingRecord ? "Edit Attraction" : "Add Attraction"}
          subtitle={
            editingRecord
              ? "Update this attraction's details."
              : "Add a new attraction to the destination database."
          }
          submitLabel={editingRecord ? "Save changes" : "Save Attraction"}
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

export default AttractionsList;
