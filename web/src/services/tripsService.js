import api from "./api";
import { TRIP_STATUS } from "../constants/tripStatus";
import {
  InvalidTripStatusError,
  statusAfterSave,
  statusAfterUnsave,
} from "../utils/tripStatus";
import { formatDate, formatDateRange, formatMoney } from "../utils/tripFormat";

function formatEditedAt(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "recently"
    : date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
}

function mapTrip(trip) {
  const status = String(trip.status || "").toUpperCase();
  const dateRange = formatDateRange(
    trip.travel_start_date,
    trip.travel_end_date,
    {
      withYear: true,
    },
  );
  const dayCount = Number(trip.duration) || 0;
  const budget = Number(trip.budget) || 0;
  const edited = formatEditedAt(trip.updated_at);
  const title =
    trip.title ||
    (status === TRIP_STATUS.DRAFT ? "Untitled trip" : `Trip · ${dateRange}`);
  const common = {
    id: trip.id,
    status,
    title,
    where:
      status === TRIP_STATUS.DRAFT
        ? "Destination not set"
        : "Loading destination…",
    edited,
    budget,
    dayCount,
    days: dayCount,
  };

  if (status === TRIP_STATUS.DRAFT) {
    return {
      ...common,
      stage: "Planning in progress",
      pct: null,
      prompt: null,
    };
  }

  return {
    ...common,
    coverImageUrl: null,
    coverHint: "Trip itinerary",
    facts: [
      { label: "Length", value: `${dayCount} days` },
      { label: "Budget", value: formatMoney(budget) },
      { label: "Updated", value: formatDate(trip.updated_at?.slice(0, 10)) },
    ],
    days: [],
  };
}

export async function listTrips() {
  const response = await api.get("/api/v1/trips");
  return response.data.data.map(mapTrip);
}

export async function getTripDetails(tripId) {
  const response = await api.get(`/api/v1/trips/${tripId}`);
  return response.data.data;
}

export async function saveTrip(tripId) {
  const response = await api.post(`/api/v1/trips/${tripId}/save`);
  return mapTrip(response.data.data);
}

export async function unsaveTrip(tripId) {
  const response = await api.delete(`/api/v1/trips/${tripId}/save`);
  return mapTrip(response.data.data);
}

export async function resumeTrip(tripId) {
  const response = await api.get(`/api/v1/trips/${tripId}/resume`);
  return response.data.data;
}

export async function renameDraftTrip(tripId, title) {
  const response = await api.patch(`/api/v1/trips/${tripId}/title`, { title });
  return mapTrip(response.data.data);
}

export async function discardDraftTrip(tripId) {
  await api.delete(`/api/v1/trips/${tripId}`);
}

// Kept as a small in-memory helper for the existing service unit tests.
// The page uses listTrips() above and does not use this helper for its data.
function apiError(status, code, message) {
  const error = new Error(message);
  error.response = {
    status,
    data: { success: false, error: { code, message, details: [] } },
  };
  return error;
}

export function createTripsService(seed) {
  let trips = seed.map((trip) => ({ ...trip }));

  function changeStatus(tripId, nextStatus) {
    const trip = trips.find((item) => item.id === tripId);
    if (!trip) throw apiError(404, "NOT_FOUND", "Trip not found.");
    let status;
    try {
      status = nextStatus(trip.status);
    } catch (error) {
      if (error instanceof InvalidTripStatusError) {
        throw apiError(400, "VALIDATION_ERROR", error.message);
      }
      throw error;
    }
    const updated = { ...trip, status };
    trips = trips.map((item) => (item.id === tripId ? updated : item));
    return { success: true, data: { ...updated } };
  }

  return {
    listTrips: () => trips.map((trip) => ({ ...trip })),
    saveTrip: async (tripId) => changeStatus(tripId, statusAfterSave),
    unsaveTrip: async (tripId) => changeStatus(tripId, statusAfterUnsave),
  };
}
