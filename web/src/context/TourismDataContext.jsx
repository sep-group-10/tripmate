import { useEffect, useState } from "react";
import { TourismDataContext } from "./tourismDataContext";
import initialAttractions from "../services/attractionsData";
import initialHotels from "../services/hotelsData";
import initialRestaurants from "../services/restaurantsData";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

function makeAdder(setItems, prefix) {
  return (record) => {
    const item = { ...record, id: `${prefix}-${crypto.randomUUID()}` };
    setItems((prev) => [item, ...prev]);
    return item;
  };
}

function makeUpdater(setItems) {
  return (id, fields) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...fields } : item)),
    );
  };
}

function makeDeleter(setItems) {
  return (id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };
}

/** Holds the 4 admin tourism entities in state. Destinations (C4.2) is
 * wired to the real API - see below. Attractions/Hotels/Restaurants are
 * still seeded from the mock data files pending their own C4.2 pass (they
 * need destination_id FK resolution, structured hours, and a real price
 * field first - see DestinationsList's report for the plan). The
 * add/update/delete functions are still the seam callers use either way,
 * mock or real. */
export function TourismDataProvider({ children }) {
  const [destinations, setDestinations] = useState([]);
  const [destinationsStatus, setDestinationsStatus] = useState("loading"); // loading | ready | error
  const [destinationsError, setDestinationsError] = useState("");

  const [attractions, setAttractions] = useState(initialAttractions);
  const [hotels, setHotels] = useState(initialHotels);
  const [restaurants, setRestaurants] = useState(initialRestaurants);

  useEffect(() => {
    let cancelled = false;
    api
      // limit=50 is the backend's max page size (Query(..., le=50)) - there
      // is no pagination UI yet, so this just pulls everything that fits in
      // one page. Fine for the current seed data; revisit if the real
      // destination count ever approaches 50.
      .get("/api/v1/destinations", { params: { limit: 50 } })
      .then((response) => {
        if (cancelled) return;
        setDestinations(response.data.data.items);
        setDestinationsStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        setDestinationsError(parseApiError(error).message);
        setDestinationsStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // These three intentionally let their errors propagate (no try/catch) -
  // DestinationsList awaits them and shows the failure in the form/dialog
  // that triggered it, rather than this context swallowing it silently.
  const addDestination = async (fields) => {
    const response = await api.post("/api/v1/destinations", fields);
    setDestinations((prev) => [response.data, ...prev]);
    return response.data;
  };

  const updateDestination = async (id, fields) => {
    const response = await api.patch(`/api/v1/destinations/${id}`, fields);
    setDestinations((prev) =>
      prev.map((item) => (item.id === id ? response.data : item)),
    );
    return response.data;
  };

  const deleteDestination = async (id) => {
    await api.delete(`/api/v1/destinations/${id}`);
    setDestinations((prev) => prev.filter((item) => item.id !== id));
  };

  const value = {
    destinations,
    destinationsStatus,
    destinationsError,
    addDestination,
    updateDestination,
    deleteDestination,
    attractions,
    hotels,
    restaurants,
    addAttraction: makeAdder(setAttractions, "attr"),
    addHotel: makeAdder(setHotels, "hotel"),
    addRestaurant: makeAdder(setRestaurants, "rest"),
    updateAttraction: makeUpdater(setAttractions),
    updateHotel: makeUpdater(setHotels),
    updateRestaurant: makeUpdater(setRestaurants),
    deleteAttraction: makeDeleter(setAttractions),
    deleteHotel: makeDeleter(setHotels),
    deleteRestaurant: makeDeleter(setRestaurants),
  };

  return (
    <TourismDataContext.Provider value={value}>
      {children}
    </TourismDataContext.Provider>
  );
}
