import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import ListPagination from "../../components/ListPagination";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";
import { parseApiError } from "../../utils/apiError";
import {
  formatCurrency,
  isDescriptionRequired,
} from "../../utils/tourismMapping";

const PAGE_SIZE = 50;

function LocalEventsList() {
  const {
    localEvents,
    localEventsStatus,
    localEventsError,
    destinations,
    addLocalEvent,
    updateLocalEvent,
    deleteLocalEvent,
    addLocalEventPhoto,
  } = useTourismData();
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
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
    return localEvents
      .filter(
        (e) =>
          destinationFilter === "All" || e.destination === destinationFilter,
      )
      .filter(
        (e) =>
          !q ||
          e.name.toLowerCase().includes(q) ||
          (e.description ?? "").toLowerCase().includes(q),
      );
  }, [localEvents, query, destinationFilter]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, pageCount);
  const visibleRecords = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );

  const formFields = useMemo(
    () => [
      {
        name: "name",
        label: "Event name",
        type: "text",
        placeholder: "e.g. Colombo Coastal Music Festival",
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
        name: "event_date",
        label: "Event date",
        type: "date",
        required: true,
      },
      {
        name: "description",
        label: "Description",
        type: "textarea",
        placeholder: "Brief description shown to travellers…",
        required: isDescriptionRequired(editingRecord),
      },
      {
        name: "entry_fee",
        label: "Entry fee (LKR)",
        type: "number",
        placeholder: "e.g. 1500",
      },
      {
        name: "duration_hours",
        label: "Duration (hours)",
        type: "number",
        placeholder: "e.g. 3",
      },
    ],
    [destinationNames, destinations, editingRecord],
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
      if (editingRecord) {
        await updateLocalEvent(editingRecord.id, values);
      } else {
        await addLocalEvent(values);
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
      await deleteLocalEvent(deletingRecord.id);
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
          Admin · Local events
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Local events
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setPage(1);
          }}
          placeholder="Search local events…"
          className="w-search"
        />
        <select
          value={destinationFilter}
          onChange={(event) => {
            setDestinationFilter(event.target.value);
            setPage(1);
          }}
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
          disabled={localEventsStatus !== "ready"}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          ＋ Add Local event
        </button>
      </div>

      {localEventsStatus === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading local events…</p>
      )}

      {localEventsStatus === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {localEventsError}
        </p>
      )}

      {localEventsStatus === "ready" && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {visibleRecords.map((event) => (
              <EntityCard
                key={event.id}
                name={event.name}
                location={event.destination}
                rating={event.rating}
                photoUrls={event.photo_urls}
                description={event.description}
                metrics={[
                  { label: "Date", value: event.event_date || "—" },
                  {
                    label: "Entry",
                    value: formatCurrency(event.entry_fee),
                  },
                  {
                    label: "Duration",
                    value: event.duration_hours
                      ? `${event.duration_hours} hr`
                      : "—",
                  },
                ]}
                onEdit={() => openEditForm(event)}
                onDelete={() => {
                  setDeleteError("");
                  setDeletingRecord(event);
                }}
              />
            ))}
          </div>
          <ListPagination
            page={currentPage}
            pageSize={PAGE_SIZE}
            total={filtered.length}
            onPageChange={setPage}
          />
        </>
      )}

      {isFormOpen && (
        <EntityFormModal
          title={editingRecord ? "Edit Local event" : "Add Local event"}
          subtitle={
            editingRecord
              ? "Update this local event's details."
              : "Add a new local event to the destination database."
          }
          submitLabel={editingRecord ? "Save changes" : "Save Local event"}
          fields={formFields}
          initialValues={editingRecord}
          onSubmit={handleSubmit}
          onClose={() => setIsFormOpen(false)}
          onUploadPhoto={
            editingRecord
              ? (file) => addLocalEventPhoto(editingRecord.id, file)
              : undefined
          }
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

export default LocalEventsList;
