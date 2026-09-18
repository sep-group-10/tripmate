import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";
import { parseApiError } from "../../utils/apiError";
import { formatCurrency } from "../../utils/tourismMapping";

// `tier` has no backend/app/schemas/tourism.py field (C4.2/C4.3) - kept
// here purely as a client-side taxonomy for the form and tag color, but
// excluded from the API payload (see utils/tourismMapping.js) rather than
// sent and silently ignored. The filter dropdown is deliberately NOT
// offered below, since filtering by an unpersisted field would silently
// return nothing for every real (API-loaded) hotel.
const TIER_OPTIONS = ["Luxury", "Boutique"];

function HotelsList() {
  const {
    hotels,
    hotelsStatus,
    hotelsError,
    destinations,
    addHotel,
    updateHotel,
    deleteHotel,
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
    return hotels
      .filter(
        (h) =>
          destinationFilter === "All" || h.destination === destinationFilter,
      )
      .filter(
        (h) =>
          !q ||
          h.name.toLowerCase().includes(q) ||
          h.description.toLowerCase().includes(q),
      );
  }, [hotels, query, destinationFilter]);

  const formFields = useMemo(
    () => [
      {
        name: "name",
        label: "Hotel name",
        type: "text",
        placeholder: "e.g. 98 Acres Resort & Spa",
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
        name: "tier",
        label: "Tier",
        type: "select",
        options: TIER_OPTIONS,
        helperText: "Not saved yet — no backend field for this.",
      },
      {
        name: "description",
        label: "Description",
        type: "textarea",
        placeholder: "Brief description shown to travellers…",
        required: true,
      },
      {
        name: "price_per_night",
        label: "Price / night (LKR)",
        type: "number",
        placeholder: "e.g. 42000",
        required: true,
      },
      {
        name: "facilitiesText",
        label: "Amenities",
        type: "text",
        placeholder: "e.g. Pool, Spa, Restaurant",
      },
    ],
    [destinationNames],
  );

  const openAddForm = () => {
    setEditingRecord(null);
    setFormError("");
    setIsFormOpen(true);
  };

  const openEditForm = (record) => {
    setEditingRecord({
      ...record,
      facilitiesText: (record.facilities || []).join(", "),
    });
    setFormError("");
    setIsFormOpen(true);
  };

  const handleSubmit = async ({ facilitiesText, ...values }) => {
    const facilities = facilitiesText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    const payload = { ...values, facilities };

    setFormSubmitting(true);
    setFormError("");
    try {
      if (editingRecord) {
        await updateHotel(editingRecord.id, payload);
      } else {
        await addHotel(payload);
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
      await deleteHotel(deletingRecord.id);
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
          Admin · Hotels
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Hotels
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search hotels…"
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
          disabled={hotelsStatus !== "ready"}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          ＋ Add Hotel
        </button>
      </div>

      {hotelsStatus === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading hotels…</p>
      )}

      {hotelsStatus === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {hotelsError}
        </p>
      )}

      {hotelsStatus === "ready" && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((hotel) => (
            <EntityCard
              key={hotel.id}
              name={hotel.name}
              location={hotel.destination}
              rating={hotel.rating}
              tag={hotel.tier ? { label: hotel.tier, tone: "warn" } : undefined}
              description={hotel.description}
              metrics={[
                {
                  label: "Price / night",
                  value: formatCurrency(hotel.price_per_night),
                },
              ]}
              chips={hotel.facilities}
              onEdit={() => openEditForm(hotel)}
              onDelete={() => {
                setDeleteError("");
                setDeletingRecord(hotel);
              }}
            />
          ))}
        </div>
      )}

      {isFormOpen && (
        <EntityFormModal
          title={editingRecord ? "Edit Hotel" : "Add Hotel"}
          subtitle={
            editingRecord
              ? "Update this hotel's details."
              : "Add a new hotel or stay to the accommodations database."
          }
          submitLabel={editingRecord ? "Save changes" : "Save Hotel"}
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

export default HotelsList;
