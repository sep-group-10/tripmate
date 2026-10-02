import { TRIP_STATUS } from "../constants/tripStatus";

// Raised when a status change isn't allowed. The message is safe to show.
export class InvalidTripStatusError extends Error {}

export function canSaveTrip(status) {
  return status === TRIP_STATUS.GENERATED;
}

// Only a GENERATED trip can be saved.
export function statusAfterSave(status) {
  if (!canSaveTrip(status)) {
    throw new InvalidTripStatusError("Only generated trips can be saved.");
  }
  return TRIP_STATUS.SAVED;
}

// Only a SAVED trip can be removed from saved; it goes back to GENERATED.
export function statusAfterUnsave(status) {
  if (status !== TRIP_STATUS.SAVED) {
    throw new InvalidTripStatusError("Only saved trips can be unsaved.");
  }
  return TRIP_STATUS.GENERATED;
}
