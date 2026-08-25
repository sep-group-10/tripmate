import { useMemo, useState } from "react";
import EntityCard from "../../components/EntityCard";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import ConfirmDeleteDialog from "../../components/ConfirmDeleteDialog";
import { useTourismData } from "../../hooks/useTourismData";

const TIER_OPTIONS = ["Luxury", "Boutique"];

function HotelsList() {
  const { hotels, destinations, addHotel, updateHotel, deleteHotel } =
    useTourismData();
  const [query, setQuery] = useState("");
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [tierFilter, setTierFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [deletingRecord, setDeletingRecord] = useState(null);

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
      .filter((h) => tierFilter === "All" || h.tier === tierFilter)
      .filter(
        (h) =>
          !q ||
          h.name.toLowerCase().includes(q) ||
          h.description.toLowerCase().includes(q),
      );
  }, [hotels, query, destinationFilter, tierFilter]);

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
        name: "pricePerNight",
        label: "Price / night",
        type: "text",
        placeholder: "e.g. LKR 28,000–55,000",
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
    setIsFormOpen(true);
  };

  const openEditForm = (record) => {
    setEditingRecord({
      ...record,
      facilitiesText: (record.facilities || []).join(", "),
    });
    setIsFormOpen(true);
  };

  const handleSubmit = ({ facilitiesText, ...values }) => {
    const facilities = facilitiesText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    if (editingRecord) {
      updateHotel(editingRecord.id, { ...values, facilities });
    } else {
      addHotel({ ...values, facilities });
    }
    setIsFormOpen(false);
  };

  const handleConfirmDelete = () => {
    deleteHotel(deletingRecord.id);
    setDeletingRecord(null);
  };

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-[11px] font-medium tracking-widest text-muted-600 uppercase">
          Admin · Hotels
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-[28px] font-semibold tracking-tight">
          Hotels
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search hotels…"
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
          value={tierFilter}
          onChange={(event) => setTierFilter(event.target.value)}
          aria-label="Tier"
          className="min-h-10 min-w-[170px] rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
        >
          <option value="All">All tiers</option>
          {TIER_OPTIONS.map((option) => (
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
          ＋ Add Hotel
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((hotel) => (
          <EntityCard
            key={hotel.id}
            name={hotel.name}
            location={hotel.destination}
            rating={hotel.rating}
            tag={{ label: hotel.tier, tone: "warn" }}
            description={hotel.description}
            metrics={[{ label: "Price / night", value: hotel.pricePerNight }]}
            chips={hotel.facilities}
            onEdit={() => openEditForm(hotel)}
            onDelete={() => setDeletingRecord(hotel)}
          />
        ))}
      </div>

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

export default HotelsList;
