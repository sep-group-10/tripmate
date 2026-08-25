import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";

const REGION_TONES = {
  "Hill Country": "success",
  "Cultural Triangle": "warn",
  Coastal: "info",
  Wildlife: "accent",
};

const REGION_CATEGORIES = Object.keys(REGION_TONES);

const FORM_FIELDS = [
  {
    name: "name",
    label: "Destination name",
    type: "text",
    placeholder: "e.g. Nuwara Eliya",
    required: true,
  },
  {
    name: "region",
    label: "Region",
    type: "text",
    placeholder: "e.g. Central Province",
    required: true,
  },
  {
    name: "country",
    label: "Country",
    type: "text",
    placeholder: "e.g. Sri Lanka",
    required: true,
  },
  {
    name: "tag",
    label: "Category",
    type: "select",
    options: REGION_CATEGORIES,
    required: true,
  },
  {
    name: "description",
    label: "Description",
    type: "textarea",
    placeholder: "Brief description shown to travellers…",
    required: true,
  },
];

function DestinationsList() {
  const { destinations, addDestination, updateDestination, deleteDestination } =
    useTourismData();
  const [query, setQuery] = useState("");
  const [regionFilter, setRegionFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [deletingRecord, setDeletingRecord] = useState(null);

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
  }, [destinations, query, regionFilter]);

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
      updateDestination(editingRecord.id, values);
    } else {
      addDestination(values);
    }
    setIsFormOpen(false);
  };

  const handleConfirmDelete = () => {
    deleteDestination(deletingRecord.id);
    setDeletingRecord(null);
  };

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
          Admin · Destinations
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Destinations
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search destinations…"
          className="w-search"
        />
        <select
          value={regionFilter}
          onChange={(event) => setRegionFilter(event.target.value)}
          aria-label="Region"
          className="min-h-10 min-w-filter rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          <option value="All">All regions</option>
          {REGION_CATEGORIES.map((option) => (
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
          ＋ Add Destination
        </button>
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
            onEdit={() => openEditForm(destination)}
            onDelete={() => setDeletingRecord(destination)}
          />
        ))}
      </div>

      {isFormOpen && (
        <EntityFormModal
          title={editingRecord ? "Edit Destination" : "Add Destination"}
          subtitle={
            editingRecord
              ? "Update this destination's details."
              : "Add a new destination to the tourism database."
          }
          submitLabel={editingRecord ? "Save changes" : "Save Destination"}
          fields={FORM_FIELDS}
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

export default DestinationsList;
