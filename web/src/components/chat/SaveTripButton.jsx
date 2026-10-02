import { Check } from "lucide-react";
import { TRIP_STATUS } from "../../constants/tripStatus";
import { canSaveTrip } from "../../utils/tripStatus";

// Planner header button. DRAFT (no itinerary yet): disabled. GENERATED: enabled.
// SAVED: a non-clickable "Saved" confirmation.
function SaveTripButton({ status, onSave }) {
  if (status === TRIP_STATUS.SAVED) {
    return (
      <span
        role="status"
        className="inline-flex items-center gap-1.5 rounded-pill bg-success-100 px-3.5 py-1.5 text-xs font-medium text-success-700"
      >
        Saved
        <Check size={14} aria-hidden="true" />
      </span>
    );
  }

  const enabled = canSaveTrip(status);
  return (
    <button
      type="button"
      onClick={onSave}
      disabled={!enabled}
      title={enabled ? undefined : "Plan a trip first"}
      className="rounded-pill bg-accent px-3.5 py-1.5 text-xs font-medium text-white shadow-control hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:bg-accent"
    >
      Save trip
    </button>
  );
}

export default SaveTripButton;
