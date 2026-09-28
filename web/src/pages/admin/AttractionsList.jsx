import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";
import { parseApiError } from "../../utils/apiError";
import { formatCurrency } from "../../utils/tourismMapping";

function AttractionsList() {
  const {
    attractions,
    attractionsStatus,
    attractionsError,
    destinations,
    addAttraction,
    updateAttraction,
    deleteAttraction,
  } = useTourismData();
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [deletingRecord, setDeletingRecord] = useState(null);
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

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
      .filter(
        (a) =>
          !q ||
          a.name.toLowerCase().includes(q) ||
          (a.description ?? "").toLowerCase().includes(q),
      );
  }, [attractions, query, destinationFilter]);

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
        name: "location",
        label: "Location",
        type: "location",
        required: true,
        resolveInitialCenter: (values) => {
          const destination = destinations.find(
            (d) => d.name === values.destination,
          );
          return destination
            ? {
                latitude: destination.latitude,
                longitude: destination.longitude,
              }
            : undefined;
        },
      },
      {
        name: "description",
        label: "Description",
        type: "textarea",
        placeholder: "Brief description shown to travellers…",
        required: true,
      },
      {
        name: "opening_hours",
        label: "Hours",
        type: "text",
        placeholder: "e.g. 06:00-18:00",
      },
      {
        name: "entry_fee",
        label: "Entry fee (LKR)",
        type: "number",
        placeholder: "e.g. 500",
      },
      {
        name: "duration_hours",
        label: "Duration (hours)",
        type: "number",
        placeholder: "e.g. 2",
      },
    ],
    [destinationNames, destinations],
  );

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
    try {
      // Carries the original per-day opening_hours dict alongside the
      // form's single displayed value, so tourismMapping's hoursForApi can
      // tell an untouched Hours field from a real edit (see C4.4 finding B).
      const payloadValues = {
        ...values,
        opening_hours_raw: editingRecord?.opening_hours_raw,
      };
      if (editingRecord) {
        await updateAttraction(editingRecord.id, payloadValues);
      } else {
        await addAttraction(payloadValues);
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
      await deleteAttraction(deletingRecord.id);
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
          Admin · Attractions
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Attractions
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search attractions…"
          className="w-search"
        />
        <select
          value={destinationFilter}
          onChange={(event) => setDestinationFilter(event.target.value)}
          aria-label="Destination"
          className="min-h-10 min-w-filter rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          <option value="All">All destinations</option>
          {destinationNames.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={openAddForm}
          disabled={attractionsStatus !== "ready"}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          ＋ Add Attraction
        </button>
      </div>

      {attractionsStatus === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading attractions…</p>
      )}

      {attractionsStatus === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {attractionsError}
        </p>
      )}

      {attractionsStatus === "ready" && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((attraction) => (
            <EntityCard
              key={attraction.id}
              name={attraction.name}
              location={attraction.destination}
              rating={attraction.rating}
              description={attraction.description}
              metrics={[
                { label: "Hours", value: attraction.opening_hours || "—" },
                { label: "Entry", value: formatCurrency(attraction.entry_fee) },
                {
                  label: "Duration",
                  value: attraction.duration_hours
                    ? `${attraction.duration_hours} hr`
                    : "—",
                },
              ]}
              onEdit={() => openEditForm(attraction)}
              onDelete={() => {
                setDeleteError("");
                setDeletingRecord(attraction);
              }}
            />
          ))}
        </div>
      )}

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

export default AttractionsList;
