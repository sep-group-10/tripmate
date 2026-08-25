import { useState } from "react";
import { TourismDataContext } from "./tourismDataContext";
import initialDestinations from "../services/destinationsData";
import initialAttractions from "../services/attractionsData";
import initialHotels from "../services/hotelsData";
import initialRestaurants from "../services/restaurantsData";

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

/** Holds the 4 admin tourism entities in state (seeded from the mock data
 * files) so records created/edited/deleted via the admin forms actually
 * show up in their list, not just get logged. C4 will swap this for real
 * API calls (delete becomes a soft-delete request); the add/update/delete
 * functions are the seam that work will land on. */
export function TourismDataProvider({ children }) {
  const [destinations, setDestinations] = useState(initialDestinations);
  const [attractions, setAttractions] = useState(initialAttractions);
  const [hotels, setHotels] = useState(initialHotels);
  const [restaurants, setRestaurants] = useState(initialRestaurants);

  const value = {
    destinations,
    attractions,
    hotels,
    restaurants,
    addDestination: makeAdder(setDestinations, "dest"),
    addAttraction: makeAdder(setAttractions, "attr"),
    addHotel: makeAdder(setHotels, "hotel"),
    addRestaurant: makeAdder(setRestaurants, "rest"),
    updateDestination: makeUpdater(setDestinations),
    updateAttraction: makeUpdater(setAttractions),
    updateHotel: makeUpdater(setHotels),
    updateRestaurant: makeUpdater(setRestaurants),
    deleteDestination: makeDeleter(setDestinations),
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
