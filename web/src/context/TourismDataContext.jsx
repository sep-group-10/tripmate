import { useEffect, useState } from "react";
import { TourismDataContext } from "./tourismDataContext";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";
import {
  buildAttractionPayload,
  mapAttractionFromApi,
  buildHotelPayload,
  mapHotelFromApi,
  buildRestaurantPayload,
  mapRestaurantFromApi,
} from "../utils/tourismMapping";

// Only GET /destinations is paginated ({success, data: {items, ...}}).
// GET /attractions|hotels|restaurants (backend/app/api/tourism.py) return a
// plain list[...Response] with no pagination at all - so those three fetch
// effects below read `response.data` directly instead of
// `response.data.data.items`.
// limit=50 is the destinations endpoint's max page size (Query(..., le=50))
// - there is no pagination UI yet, so this just pulls everything that fits
// in one page. Fine for the current seed data; revisit if the real
// destination count ever approaches 50.
const DESTINATION_LIST_PARAMS = { params: { limit: 50 } };

/** Holds the 4 admin tourism entities in state, all wired to the real API
 * (C4.2). Attractions/Hotels/Restaurants each depend on `destinations`
 * being loaded first, since every add/update needs it to resolve
 * destination_id and coordinates (see utils/tourismMapping.js) - their
 * fetch effects wait on `destinationsStatus`. */
export function TourismDataProvider({ children }) {
  const [destinations, setDestinations] = useState([]);
  const [destinationsStatus, setDestinationsStatus] = useState("loading"); // loading | ready | error
  const [destinationsError, setDestinationsError] = useState("");

  const [attractions, setAttractions] = useState([]);
  const [attractionsStatus, setAttractionsStatus] = useState("loading");
  const [attractionsError, setAttractionsError] = useState("");

  const [hotels, setHotels] = useState([]);
  const [hotelsStatus, setHotelsStatus] = useState("loading");
  const [hotelsError, setHotelsError] = useState("");

  const [restaurants, setRestaurants] = useState([]);
  const [restaurantsStatus, setRestaurantsStatus] = useState("loading");
  const [restaurantsError, setRestaurantsError] = useState("");

  useEffect(() => {
    let cancelled = false;
    api
      .get("/api/v1/destinations", DESTINATION_LIST_PARAMS)
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

  useEffect(() => {
    if (destinationsStatus !== "ready") return;
    let cancelled = false;
    api
      .get("/api/v1/attractions")
      .then((response) => {
        if (cancelled) return;
        setAttractions(
          response.data.map((item) => mapAttractionFromApi(item, destinations)),
        );
        setAttractionsStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        setAttractionsError(parseApiError(error).message);
        setAttractionsStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [destinationsStatus, destinations]);

  useEffect(() => {
    if (destinationsStatus !== "ready") return;
    let cancelled = false;
    api
      .get("/api/v1/hotels")
      .then((response) => {
        if (cancelled) return;
        setHotels(
          response.data.map((item) => mapHotelFromApi(item, destinations)),
        );
        setHotelsStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        setHotelsError(parseApiError(error).message);
        setHotelsStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [destinationsStatus, destinations]);

  useEffect(() => {
    if (destinationsStatus !== "ready") return;
    let cancelled = false;
    api
      .get("/api/v1/restaurants")
      .then((response) => {
        if (cancelled) return;
        setRestaurants(
          response.data.map((item) => mapRestaurantFromApi(item, destinations)),
        );
        setRestaurantsStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        setRestaurantsError(parseApiError(error).message);
        setRestaurantsStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [destinationsStatus, destinations]);

  // All add/update/delete functions below intentionally let their errors
  // propagate (no try/catch) - the *List components await them and show the
  // failure in the form/dialog that triggered it, rather than this context
  // swallowing it silently.
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

  const addAttraction = async (values) => {
    const response = await api.post(
      "/api/v1/attractions",
      buildAttractionPayload(values, destinations),
    );
    const mapped = mapAttractionFromApi(response.data, destinations);
    setAttractions((prev) => [mapped, ...prev]);
    return mapped;
  };

  const updateAttraction = async (id, values) => {
    const response = await api.patch(
      `/api/v1/attractions/${id}`,
      buildAttractionPayload(values, destinations),
    );
    const mapped = mapAttractionFromApi(response.data, destinations);
    setAttractions((prev) =>
      prev.map((item) => (item.id === id ? mapped : item)),
    );
    return mapped;
  };

  const deleteAttraction = async (id) => {
    await api.delete(`/api/v1/attractions/${id}`);
    setAttractions((prev) => prev.filter((item) => item.id !== id));
  };

  const addHotel = async (values) => {
    const response = await api.post(
      "/api/v1/hotels",
      buildHotelPayload(values, destinations),
    );
    const mapped = mapHotelFromApi(response.data, destinations);
    setHotels((prev) => [mapped, ...prev]);
    return mapped;
  };

  const updateHotel = async (id, values) => {
    const response = await api.patch(
      `/api/v1/hotels/${id}`,
      buildHotelPayload(values, destinations),
    );
    const mapped = mapHotelFromApi(response.data, destinations);
    setHotels((prev) => prev.map((item) => (item.id === id ? mapped : item)));
    return mapped;
  };

  const deleteHotel = async (id) => {
    await api.delete(`/api/v1/hotels/${id}`);
    setHotels((prev) => prev.filter((item) => item.id !== id));
  };

  const addRestaurant = async (values) => {
    const response = await api.post(
      "/api/v1/restaurants",
      buildRestaurantPayload(values, destinations),
    );
    const mapped = mapRestaurantFromApi(response.data, destinations);
    setRestaurants((prev) => [mapped, ...prev]);
    return mapped;
  };

  const updateRestaurant = async (id, values) => {
    const response = await api.patch(
      `/api/v1/restaurants/${id}`,
      buildRestaurantPayload(values, destinations),
    );
    const mapped = mapRestaurantFromApi(response.data, destinations);
    setRestaurants((prev) =>
      prev.map((item) => (item.id === id ? mapped : item)),
    );
    return mapped;
  };

  const deleteRestaurant = async (id) => {
    await api.delete(`/api/v1/restaurants/${id}`);
    setRestaurants((prev) => prev.filter((item) => item.id !== id));
  };

  const value = {
    destinations,
    destinationsStatus,
    destinationsError,
    addDestination,
    updateDestination,
    deleteDestination,
    attractions,
    attractionsStatus,
    attractionsError,
    addAttraction,
    updateAttraction,
    deleteAttraction,
    hotels,
    hotelsStatus,
    hotelsError,
    addHotel,
    updateHotel,
    deleteHotel,
    restaurants,
    restaurantsStatus,
    restaurantsError,
    addRestaurant,
    updateRestaurant,
    deleteRestaurant,
  };

  return (
    <TourismDataContext.Provider value={value}>
      {children}
    </TourismDataContext.Provider>
  );
}
