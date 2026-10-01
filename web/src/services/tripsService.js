import { MY_TRIPS } from "../data/myTripsDummyData";
import {
  InvalidTripStatusError,
  statusAfterSave,
  statusAfterUnsave,
} from "../utils/tripStatus";

// MOCK trips service: an in-memory store seeded from MY_TRIPS, so a change made
// on one page is visible on another until the page reloads. There is no trips
// endpoint yet. TODO(backend): replace the bodies of saveTrip and unsaveTrip
// with POST /api/v1/trips/{id}/save and DELETE /api/v1/trips/{id}/save, return
// the standard { success, data } response from the shared axios client
// (services/api.js), and load the list from GET /api/v1/trips.

// Builds the error an axios call would reject with for a failed API request,
// so callers can use parseApiError (utils/apiError.js) unchanged. The contract
// (docs/api-contract.md) has no "wrong state" code, so this uses
// VALIDATION_ERROR (400); a dedicated code can replace it if the backend adds one.
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
    // Sync for now; will become an async GET /api/v1/trips call.
    listTrips: () => trips.map((trip) => ({ ...trip })),
    // GENERATED -> SAVED. Rejects for DRAFT, SAVED and unknown trips.
    saveTrip: async (tripId) => changeStatus(tripId, statusAfterSave),
    // SAVED -> GENERATED. Rejects for DRAFT, GENERATED and unknown trips.
    unsaveTrip: async (tripId) => changeStatus(tripId, statusAfterUnsave),
  };
}

const tripsService = createTripsService(MY_TRIPS);

export const { listTrips, saveTrip, unsaveTrip } = tripsService;
