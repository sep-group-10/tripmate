// Bridges the admin Attractions/Hotels/Restaurants forms (name-based
// destination, single free-text hours, plain price numbers) and the real
// backend/app/schemas/tourism.py contract (destination_id FK, a per-weekday
// opening_hours/operating_hours dict, Decimal price fields). Kept as pure
// functions, separate from the list components, so the mapping itself is
// unit-testable without rendering anything.

const WEEKDAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

// C4.4 finding C: Description stays required for a new record, but an
// existing record whose description is already null/blank (e.g. the 15
// seeded restaurants with description: null) shouldn't be un-editable
// until an admin invents text for it. Editing a record that already has
// a real description and blanking it is still blocked.
export function isDescriptionRequired(editingRecord) {
  if (!editingRecord) return true;
  return Boolean(editingRecord.description?.trim());
}

export function findDestinationByName(destinations, name) {
  return destinations.find((destination) => destination.name === name);
}

export function findDestinationNameById(destinations, destinationId) {
  return (
    destinations.find((destination) => destination.id === destinationId)
      ?.name ?? ""
  );
}

// The admin form only collects one hours string (e.g. "08:00-18:00"), while
// the backend stores hours per weekday. We apply that single string to every
// day rather than exposing 7 inputs - callers can move to a real per-day
// editor later without changing this contract.
export function hoursTextToApi(text) {
  const trimmed = (text ?? "").trim();
  if (!trimmed) return undefined;
  return Object.fromEntries(WEEKDAYS.map((day) => [day, trimmed]));
}

export function hoursApiToText(hoursDict) {
  if (!hoursDict) return "";
  return hoursDict.monday ?? Object.values(hoursDict)[0] ?? "";
}

// The admin form only ever shows/edits a single hours string, but the
// backend dict can hold genuinely different per-day values (set outside
// this form, e.g. via seed data or a future per-day editor). If the
// displayed text still matches what that original dict would produce,
// the admin hasn't touched Hours - send the original dict back untouched
// instead of collapsing every day to the one visible value. Only a real
// edit to the text (or a brand-new record, with no original dict) causes
// hoursTextToApi to fan the new value out to all 7 days.
// On create, a blank optional field is simply omitted (undefined - dropped
// from the JSON body, backend applies its own default). On update, a blank
// value means the admin actively cleared a field that used to hold
// something, and omitting it would do nothing: the backend's update
// endpoints read the body with exclude_unset=True, so an absent key is
// "leave this alone," not "clear this." Only an explicit null clears it.
export function hoursForApi(text, originalDict, isUpdate = false) {
  const trimmed = (text ?? "").trim();
  if (!trimmed) return isUpdate ? null : undefined;
  if (originalDict && hoursApiToText(originalDict) === trimmed) {
    return originalDict;
  }
  return hoursTextToApi(trimmed);
}

// Same reasoning as hoursForApi, for the plain optional number fields
// (entry_fee, duration_hours). Never used for a field that's required in
// its form config (e.g. avg_meal_cost, price_per_night) - those are always
// numeric and never blank, so they don't need this distinction.
function optionalNumberForApi(value, isUpdate = false) {
  if (value === "" || value === null || value === undefined) {
    return isUpdate ? null : undefined;
  }
  return Number(value);
}

// Decimal fields arrive from the API as numeric-looking strings (e.g.
// "1500.00"); form number inputs want a plain numeric string.
export function decimalToFormValue(value) {
  if (value === null || value === undefined || value === "") return "";
  const num = Number(value);
  return Number.isNaN(num) ? "" : String(num);
}

export function formatCurrency(value) {
  if (value === null || value === undefined || value === "") return "—";
  const num = Number(value);
  if (Number.isNaN(num)) return "—";
  return `LKR ${num.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;
}

function requireDestination(destinations, name) {
  const destination = findDestinationByName(destinations, name);
  if (!destination) {
    throw new Error(`Unknown destination: ${name}`);
  }
  return destination;
}

// The admin's LocationPicker (web/src/components/LocationPicker.jsx) is a
// required field producing `values.location = { latitude, longitude }` from
// a real place search - this is the actual entity location, which may sit
// anywhere within (or near) the chosen destination, not the destination's
// own coordinates.
function requireLocation(location) {
  if (!location || location.latitude == null || location.longitude == null) {
    throw new Error("A location must be picked before saving.");
  }
  return location;
}

// On update, a blank description means the admin left an already-blank
// field alone (see isDescriptionRequired - editing blocks blanking a real
// description, so this only fires for a record that had none to begin
// with). Omit the key entirely so exclude_unset=True leaves the existing
// null as-is, rather than overwriting it with an empty string - an empty
// string is a valid value for this field on the backend (no min_length),
// so sending it would silently replace null with "". Create still
// requires text, so this is a no-op there.
function descriptionForApi(text, isUpdate) {
  const trimmed = (text ?? "").trim();
  if (!trimmed && isUpdate) return undefined;
  return trimmed;
}

export function buildAttractionPayload(
  values,
  destinations,
  { isUpdate = false } = {},
) {
  const destination = requireDestination(destinations, values.destination);
  const location = requireLocation(values.location);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: descriptionForApi(values.description, isUpdate),
    latitude: location.latitude,
    longitude: location.longitude,
    opening_hours: hoursForApi(
      values.opening_hours,
      values.opening_hours_raw,
      isUpdate,
    ),
    entry_fee: optionalNumberForApi(values.entry_fee, isUpdate),
    duration_hours: optionalNumberForApi(values.duration_hours, isUpdate),
  };
}

export function mapAttractionFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    location: {
      latitude: Number(record.latitude),
      longitude: Number(record.longitude),
    },
    opening_hours: hoursApiToText(record.opening_hours),
    opening_hours_raw: record.opening_hours,
    entry_fee: decimalToFormValue(record.entry_fee),
    duration_hours: decimalToFormValue(record.duration_hours),
  };
}

export function buildHotelPayload(
  values,
  destinations,
  { isUpdate = false } = {},
) {
  const destination = requireDestination(destinations, values.destination);
  const location = requireLocation(values.location);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: descriptionForApi(values.description, isUpdate),
    latitude: location.latitude,
    longitude: location.longitude,
    price_per_night: Number(values.price_per_night),
    facilities: values.facilities,
  };
}

export function mapHotelFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    location: {
      latitude: Number(record.latitude),
      longitude: Number(record.longitude),
    },
    price_per_night: decimalToFormValue(record.price_per_night),
  };
}

export function buildRestaurantPayload(
  values,
  destinations,
  { isUpdate = false } = {},
) {
  const destination = requireDestination(destinations, values.destination);
  const location = requireLocation(values.location);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: descriptionForApi(values.description, isUpdate),
    latitude: location.latitude,
    longitude: location.longitude,
    cuisine_type: values.cuisine_type,
    // avg_meal_cost is required in the form (RestaurantsList.jsx), so it can
    // never actually be blank here - no optionalNumberForApi needed.
    avg_meal_cost: Number(values.avg_meal_cost),
    operating_hours: hoursForApi(
      values.operating_hours,
      values.operating_hours_raw,
      isUpdate,
    ),
  };
}

export function mapRestaurantFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    location: {
      latitude: Number(record.latitude),
      longitude: Number(record.longitude),
    },
    operating_hours: hoursApiToText(record.operating_hours),
    operating_hours_raw: record.operating_hours,
    avg_meal_cost: decimalToFormValue(record.avg_meal_cost),
  };
}

export function buildLocalEventPayload(
  values,
  destinations,
  { isUpdate = false } = {},
) {
  const destination = requireDestination(destinations, values.destination);
  const location = requireLocation(values.location);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: descriptionForApi(values.description, isUpdate),
    latitude: location.latitude,
    longitude: location.longitude,
    entry_fee: optionalNumberForApi(values.entry_fee, isUpdate),
    duration_hours: optionalNumberForApi(values.duration_hours, isUpdate),
    event_schedule: { date: values.event_date },
  };
}

export function mapLocalEventFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    location: {
      latitude: Number(record.latitude),
      longitude: Number(record.longitude),
    },
    entry_fee: decimalToFormValue(record.entry_fee),
    duration_hours: decimalToFormValue(record.duration_hours),
    event_date: record.event_schedule?.date ?? "",
  };
}
