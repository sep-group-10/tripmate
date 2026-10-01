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

const CUISINE_TONES = {
  "Sri Lankan": "warn",
  Seafood: "info",
  International: "accent",
  "Street Food": "success",
};

const CUISINE_OPTIONS = Object.keys(CUISINE_TONES);

const PAGE_SIZE = 50;

function RestaurantsList() {
  const {
    restaurants,
    restaurantsStatus,
    restaurantsError,
    destinations,
    addRestaurant,
    updateRestaurant,
    deleteRestaurant,
    addRestaurantPhoto,
  } = useTourismData();
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [destinationFilter, setDestinationFilter] = useState("All");
  const [cuisineFilter, setCuisineFilter] = useState("All");
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
    return restaurants
      .filter(
        (r) =>
          destinationFilter === "All" || r.destination === destinationFilter,
      )
      .filter(
        (r) => cuisineFilter === "All" || r.cuisine_type === cuisineFilter,
      )
      .filter(
        (r) =>
          !q ||
          r.name.toLowerCase().includes(q) ||
          (r.description ?? "").toLowerCase().includes(q),
      );
  }, [restaurants, query, destinationFilter, cuisineFilter]);
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
        name: "cuisine_type",
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
        required: isDescriptionRequired(editingRecord),
      },
      {
        name: "operating_hours",
        label: "Hours",
        type: "text",
        placeholder: "e.g. 11:30-23:00",
      },
      {
        name: "avg_meal_cost",
        label: "Average meal cost (LKR)",
        type: "number",
        placeholder: "e.g. 2000",
        required: true,
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
      // Carries the original per-day operating_hours dict alongside the
      // form's single displayed value, so tourismMapping's hoursForApi can
      // tell an untouched Hours field from a real edit (see C4.4 finding B).
      const payloadValues = {
        ...values,
        operating_hours_raw: editingRecord?.operating_hours_raw,
      };
      if (editingRecord) {
        await updateRestaurant(editingRecord.id, payloadValues);
      } else {
        await addRestaurant(payloadValues);
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
      await deleteRestaurant(deletingRecord.id);
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
          Admin · Restaurants
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Restaurants
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setPage(1);
          }}
          placeholder="Search restaurants…"
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
        <select
          value={cuisineFilter}
          onChange={(event) => {
            setCuisineFilter(event.target.value);
            setPage(1);
          }}
          aria-label="Cuisine"
          className="min-h-10 min-w-filter rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none"
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
          disabled={restaurantsStatus !== "ready"}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          ＋ Add Restaurant
        </button>
      </div>

      {restaurantsStatus === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading restaurants…</p>
      )}

      {restaurantsStatus === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {restaurantsError}
        </p>
      )}

      {restaurantsStatus === "ready" && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {visibleRecords.map((restaurant) => (
              <EntityCard
                key={restaurant.id}
                name={restaurant.name}
                location={restaurant.destination}
                rating={restaurant.rating}
                tag={{
                  label: restaurant.cuisine_type,
                  tone: CUISINE_TONES[restaurant.cuisine_type] || "accent",
                }}
                photoUrls={restaurant.photo_urls}
                description={restaurant.description}
                metrics={[
                  { label: "Hours", value: restaurant.operating_hours || "—" },
                  {
                    label: "Avg. meal cost",
                    value: formatCurrency(restaurant.avg_meal_cost),
                  },
                ]}
                onEdit={() => openEditForm(restaurant)}
                onDelete={() => {
                  setDeleteError("");
                  setDeletingRecord(restaurant);
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
          onUploadPhoto={
            editingRecord
              ? (file) => addRestaurantPhoto(editingRecord.id, file)
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

export default RestaurantsList;
