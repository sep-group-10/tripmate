import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";
import { parseApiError } from "../../utils/apiError";
import { validateLatitude, validateLongitude } from "../../utils/validation";

// `region` here is the real backend/app/models/destination.py field (e.g.
// "Central Province") - filtering by it replaces the old mock-only
// "category" concept ("Cultural Triangle", "Hill Country", ...), which had
// no backend equivalent and doesn't make sense against real province names.
// Options are derived from whatever's actually in the fetched data rather
// than a hardcoded list, since real regions aren't a fixed enum.
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
    name: "description",
    label: "Description",
    type: "textarea",
    placeholder: "Brief description shown to travellers…",
    required: true,
  },
  {
    name: "latitude",
    label: "Latitude",
    type: "number",
    placeholder: "e.g. 6.9271",
    required: true,
    validate: validateLatitude,
  },
  {
    name: "longitude",
    label: "Longitude",
    type: "number",
    placeholder: "e.g. 79.8612",
    required: true,
    validate: validateLongitude,
  },
];

function DestinationsList() {
  const {
    destinations,
    destinationsStatus,
    destinationsError,
    addDestination,
    updateDestination,
    deleteDestination,
  } = useTourismData();
  const [query, setQuery] = useState("");
  const [regionFilter, setRegionFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [deletingRecord, setDeletingRecord] = useState(null);
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const regionOptions = useMemo(
    () =>
      Array.from(
        new Set(destinations.map((d) => d.region).filter(Boolean)),
      ).sort(),
    [destinations],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return destinations
      .filter((d) => regionFilter === "All" || d.region === regionFilter)
      .filter(
        (d) =>
          !q ||
          d.name.toLowerCase().includes(q) ||
          (d.description ?? "").toLowerCase().includes(q),
      );
  }, [destinations, query, regionFilter]);

  const openAddForm = () => {
    setEditingRecord(null);
    setFormError("");
    setIsFormOpen(true);
  };

  const openEditForm = (record) => {
    setEditingRecord(record);
    setFormError("");
    setIsFormOpen(true);
  };

  const handleSubmit = async (values) => {
    setFormSubmitting(true);
    setFormError("");
    const payload = {
      name: values.name.trim(),
      region: values.region.trim(),
      country: values.country.trim(),
      description: values.description.trim(),
      latitude: Number(values.latitude),
      longitude: Number(values.longitude),
    };
    try {
      if (editingRecord) {
        await updateDestination(editingRecord.id, payload);
      } else {
        await addDestination(payload);
      }
      setIsFormOpen(false);
    } catch (error) {
      setFormError(parseApiError(error).message);
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleConfirmDelete = async () => {
    setDeleteSubmitting(true);
    setDeleteError("");
    try {
      await deleteDestination(deletingRecord.id);
      setDeletingRecord(null);
    } catch (error) {
      setDeleteError(parseApiError(error).message);
    } finally {
      setDeleteSubmitting(false);
    }
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
          {regionOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={openAddForm}
          disabled={destinationsStatus !== "ready"}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          ＋ Add Destination
        </button>
      </div>

      {destinationsStatus === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading destinations…</p>
      )}

      {destinationsStatus === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {destinationsError}
        </p>
      )}

      {destinationsStatus === "ready" && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((destination) => (
            <EntityCard
              key={destination.id}
              name={destination.name}
              location={`${destination.region}, ${destination.country}`}
              rating={destination.rating}
              description={destination.description}
              metrics={[
                { label: "Region", value: destination.region },
                { label: "Country", value: destination.country },
              ]}
              onEdit={() => openEditForm(destination)}
              onDelete={() => {
                setDeleteError("");
                setDeletingRecord(destination);
              }}
            />
          ))}
        </div>
      )}

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
          submitting={formSubmitting}
          submitError={formError}
        />
      )}

      {deletingRecord && (
        <ConfirmDeleteDialog
          recordName={deletingRecord.name}
          onConfirm={handleConfirmDelete}
          onClose={() => setDeletingRecord(null)}
          submitting={deleteSubmitting}
          submitError={deleteError}
        />
      )}
    </div>
  );
}

export default DestinationsList;
