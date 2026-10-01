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

// Destinations use a paginated backend response. Load each page so admin
// forms still have every destination available for their selectors; the list
// page itself applies simple client-side Previous/Next paging consistently
// with Attractions, Hotels, and Restaurants.
const DESTINATION_PAGE_SIZE = 50;

/** Holds the 4 admin tourism entities in state, all wired to the real API
 * (C4.2). Attractions/Hotels/Restaurants each depend on `destinations`
 * being loaded first, since every add/update needs it to resolve
 * destination_id (see utils/tourismMapping.js) - their fetch effects wait
 * on `destinationsStatus`. Each entity's actual latitude/longitude comes
 * from its own LocationPicker field (web/src/components/LocationPicker.jsx),
 * not from the destination. */
export function TourismDataProvider({ children }) {
  const [destinations, setDestinations] = useState([]);
  const [destinationsTotal, setDestinationsTotal] = useState(0);
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
    const fetchDestinations = async () => {
      try {
        const firstResponse = await api.get("/api/v1/destinations", {
          params: { page: 1, limit: DESTINATION_PAGE_SIZE },
        });
        const firstPage = firstResponse.data.data;
        const remainingPages = await Promise.all(
          Array.from(
            { length: Math.max(0, firstPage.total_pages - 1) },
            (_, index) =>
              api.get("/api/v1/destinations", {
                params: { page: index + 2, limit: DESTINATION_PAGE_SIZE },
              }),
          ),
        );
        if (cancelled) return;
        setDestinations([
          ...firstPage.items,
          ...remainingPages.flatMap((page) => page.data.data.items),
        ]);
        setDestinationsTotal(firstPage.total);
        setDestinationsStatus("ready");
      } catch (error) {
        if (cancelled) return;
        setDestinationsError(parseApiError(error).message);
        setDestinationsStatus("error");
      }
    };
    fetchDestinations();
    return () => {
      cancelled = true;
    };
  }, []);

  // If the destinations fetch above fails, destinationsStatus never reaches
  // "ready" - the fetch effects below wait on that and would otherwise stay
  // in "loading" forever with no error shown. Adjusted during render (React's
  // own pattern for deriving state from a prop/state change) rather than in
  // an effect, since it's a plain derivation with no external system to
  // synchronize with.
  if (destinationsStatus === "error" && attractionsStatus !== "error") {
    setAttractionsError(
      "Couldn't load destinations, so attractions can't be shown.",
    );
    setAttractionsStatus("error");
  }
  if (destinationsStatus === "error" && hotelsStatus !== "error") {
    setHotelsError("Couldn't load destinations, so hotels can't be shown.");
    setHotelsStatus("error");
  }
  if (destinationsStatus === "error" && restaurantsStatus !== "error") {
    setRestaurantsError(
      "Couldn't load destinations, so restaurants can't be shown.",
    );
    setRestaurantsStatus("error");
  }

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
    setDestinationsTotal((prev) => prev + 1);
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
    setDestinationsTotal((prev) => Math.max(0, prev - 1));
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
      buildAttractionPayload(values, destinations, { isUpdate: true }),
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

  const addAttractionPhoto = async (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post(
      `/api/v1/attractions/${id}/photos`,
      formData,
    );
    const mapped = mapAttractionFromApi(response.data, destinations);
    setAttractions((prev) =>
      prev.map((item) => (item.id === id ? mapped : item)),
    );
    return mapped;
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
      buildHotelPayload(values, destinations, { isUpdate: true }),
    );
    const mapped = mapHotelFromApi(response.data, destinations);
    setHotels((prev) => prev.map((item) => (item.id === id ? mapped : item)));
    return mapped;
  };

  const deleteHotel = async (id) => {
    await api.delete(`/api/v1/hotels/${id}`);
    setHotels((prev) => prev.filter((item) => item.id !== id));
  };

  const addHotelPhoto = async (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post(`/api/v1/hotels/${id}/photos`, formData);
    const mapped = mapHotelFromApi(response.data, destinations);
    setHotels((prev) => prev.map((item) => (item.id === id ? mapped : item)));
    return mapped;
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
      buildRestaurantPayload(values, destinations, { isUpdate: true }),
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

  const addRestaurantPhoto = async (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post(
      `/api/v1/restaurants/${id}/photos`,
      formData,
    );
    const mapped = mapRestaurantFromApi(response.data, destinations);
    setRestaurants((prev) =>
      prev.map((item) => (item.id === id ? mapped : item)),
    );
    return mapped;
  };

  const value = {
    destinations,
    destinationsTotal,
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
    addAttractionPhoto,
    hotels,
    hotelsStatus,
    hotelsError,
    addHotel,
    updateHotel,
    deleteHotel,
    addHotelPhoto,
    restaurants,
    restaurantsStatus,
    restaurantsError,
    addRestaurant,
    updateRestaurant,
    addRestaurantPhoto,
    deleteRestaurant,
  };

  return (
    <TourismDataContext.Provider value={value}>
      {children}
    </TourismDataContext.Provider>
  );
}
