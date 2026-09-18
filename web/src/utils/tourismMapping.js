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

// `category` has no backend field (AttractionCreate/Update in
// schemas/tourism.py) - deliberately left out of the payload rather than
// sent and silently ignored by the API. AttractionsList flags this to the
// admin via the form's helper text instead.
export function buildAttractionPayload(values, destinations) {
  const destination = requireDestination(destinations, values.destination);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: values.description.trim(),
    latitude: destination.latitude,
    longitude: destination.longitude,
    opening_hours: hoursTextToApi(values.opening_hours),
    entry_fee: values.entry_fee === "" ? undefined : Number(values.entry_fee),
    duration_hours:
      values.duration_hours === "" ? undefined : Number(values.duration_hours),
  };
}

export function mapAttractionFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    opening_hours: hoursApiToText(record.opening_hours),
    entry_fee: decimalToFormValue(record.entry_fee),
    duration_hours: decimalToFormValue(record.duration_hours),
  };
}

// `tier` has no backend field (HotelCreate/Update) - same reasoning as
// `category` above.
export function buildHotelPayload(values, destinations) {
  const destination = requireDestination(destinations, values.destination);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: values.description.trim(),
    latitude: destination.latitude,
    longitude: destination.longitude,
    price_per_night: Number(values.price_per_night),
    facilities: values.facilities,
  };
}

export function mapHotelFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    price_per_night: decimalToFormValue(record.price_per_night),
  };
}

export function buildRestaurantPayload(values, destinations) {
  const destination = requireDestination(destinations, values.destination);
  return {
    destination_id: destination.id,
    name: values.name.trim(),
    description: values.description.trim(),
    latitude: destination.latitude,
    longitude: destination.longitude,
    cuisine_type: values.cuisine_type,
    avg_meal_cost: Number(values.avg_meal_cost),
    operating_hours: hoursTextToApi(values.operating_hours),
  };
}

export function mapRestaurantFromApi(record, destinations) {
  return {
    ...record,
    destination: findDestinationNameById(destinations, record.destination_id),
    operating_hours: hoursApiToText(record.operating_hours),
    avg_meal_cost: decimalToFormValue(record.avg_meal_cost),
  };
}
