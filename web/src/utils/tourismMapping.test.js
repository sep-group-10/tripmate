import { describe, it, expect } from "vitest";
import {
  findDestinationByName,
  findDestinationNameById,
  hoursTextToApi,
  hoursApiToText,
  decimalToFormValue,
  formatCurrency,
  buildAttractionPayload,
  mapAttractionFromApi,
  buildHotelPayload,
  mapHotelFromApi,
  buildRestaurantPayload,
  mapRestaurantFromApi,
} from "./tourismMapping";

const destinations = [
  { id: "dest-1", name: "Ella", latitude: "6.8667", longitude: "81.0466" },
  { id: "dest-2", name: "Kandy", latitude: "7.2906", longitude: "80.6337" },
];

describe("findDestinationByName / findDestinationNameById", () => {
  it("finds a destination by name", () => {
    expect(findDestinationByName(destinations, "Kandy")).toBe(destinations[1]);
  });

  it("returns undefined for an unknown name", () => {
    expect(findDestinationByName(destinations, "Nowhere")).toBeUndefined();
  });

  it("resolves a destination_id back to its name", () => {
    expect(findDestinationNameById(destinations, "dest-1")).toBe("Ella");
  });

  it("returns an empty string for an unknown id", () => {
    expect(findDestinationNameById(destinations, "missing")).toBe("");
  });
});

describe("hoursTextToApi / hoursApiToText", () => {
  it("applies a single hours string to every weekday", () => {
    const dict = hoursTextToApi("08:00-18:00");
    expect(dict.monday).toBe("08:00-18:00");
    expect(dict.sunday).toBe("08:00-18:00");
    expect(Object.keys(dict)).toHaveLength(7);
  });

  it("returns undefined for blank input so the field stays optional", () => {
    expect(hoursTextToApi("")).toBeUndefined();
    expect(hoursTextToApi("   ")).toBeUndefined();
  });

  it("reads monday back out of an hours dict", () => {
    expect(hoursApiToText({ monday: "08:00-18:00" })).toBe("08:00-18:00");
  });

  it("falls back to the first value when monday is missing", () => {
    expect(hoursApiToText({ tuesday: "09:00-17:00" })).toBe("09:00-17:00");
  });

  it("returns an empty string for a null dict", () => {
    expect(hoursApiToText(null)).toBe("");
  });
});

describe("decimalToFormValue / formatCurrency", () => {
  it("converts a Decimal-as-string into a plain numeric string", () => {
    expect(decimalToFormValue("1500.00")).toBe("1500");
  });

  it("treats null/empty as an empty form value", () => {
    expect(decimalToFormValue(null)).toBe("");
    expect(decimalToFormValue("")).toBe("");
  });

  it("formats a numeric value as LKR currency", () => {
    expect(formatCurrency("1500.00")).toBe("LKR 1,500");
  });

  it("formats missing values as an em dash", () => {
    expect(formatCurrency(null)).toBe("—");
    expect(formatCurrency("not-a-number")).toBe("—");
  });
});

describe("buildAttractionPayload / mapAttractionFromApi", () => {
  it("resolves destination_id and coordinates from the destination name", () => {
    const payload = buildAttractionPayload(
      {
        name: " Nine Arch Bridge ",
        destination: "Ella",
        description: " A viaduct. ",
        opening_hours: "06:00-18:00",
        entry_fee: "500",
        duration_hours: "2",
      },
      destinations,
    );
    expect(payload).toEqual({
      destination_id: "dest-1",
      name: "Nine Arch Bridge",
      description: "A viaduct.",
      latitude: "6.8667",
      longitude: "81.0466",
      opening_hours: hoursTextToApi("06:00-18:00"),
      entry_fee: 500,
      duration_hours: 2,
    });
  });

  it("omits entry_fee/duration_hours when left blank", () => {
    const payload = buildAttractionPayload(
      {
        name: "Ella Rock",
        destination: "Ella",
        description: "A hike.",
        opening_hours: "",
        entry_fee: "",
        duration_hours: "",
      },
      destinations,
    );
    expect(payload.entry_fee).toBeUndefined();
    expect(payload.duration_hours).toBeUndefined();
    expect(payload.opening_hours).toBeUndefined();
  });

  it("throws for a destination that isn't in the list", () => {
    expect(() =>
      buildAttractionPayload(
        { name: "X", destination: "Nowhere", description: "" },
        destinations,
      ),
    ).toThrow(/Unknown destination/);
  });

  it("maps an API attraction record back to form-friendly values", () => {
    const record = {
      id: "attr-1",
      destination_id: "dest-2",
      name: "Temple of the Tooth",
      entry_fee: "1500.00",
      duration_hours: "2.00",
      opening_hours: { monday: "05:30-20:00" },
    };
    expect(mapAttractionFromApi(record, destinations)).toEqual({
      ...record,
      destination: "Kandy",
      opening_hours: "05:30-20:00",
      entry_fee: "1500",
      duration_hours: "2",
    });
  });
});

describe("buildHotelPayload / mapHotelFromApi", () => {
  it("builds a hotel payload with a numeric price and facilities array", () => {
    const payload = buildHotelPayload(
      {
        name: "98 Acres Resort",
        destination: "Ella",
        description: "A resort.",
        price_per_night: "42000",
        facilities: ["Pool", "Spa"],
      },
      destinations,
    );
    expect(payload).toEqual({
      destination_id: "dest-1",
      name: "98 Acres Resort",
      description: "A resort.",
      latitude: "6.8667",
      longitude: "81.0466",
      price_per_night: 42000,
      facilities: ["Pool", "Spa"],
    });
  });

  it("maps an API hotel record back to form-friendly values", () => {
    const record = {
      id: "hotel-1",
      destination_id: "dest-1",
      name: "98 Acres Resort",
      price_per_night: "42000.00",
      facilities: ["Pool"],
    };
    expect(mapHotelFromApi(record, destinations)).toEqual({
      ...record,
      destination: "Ella",
      price_per_night: "42000",
    });
  });
});

describe("buildRestaurantPayload / mapRestaurantFromApi", () => {
  it("builds a restaurant payload with a numeric avg_meal_cost", () => {
    const payload = buildRestaurantPayload(
      {
        name: "Cafe Chill",
        destination: "Ella",
        description: "A cafe.",
        cuisine_type: "International",
        avg_meal_cost: "2000",
        operating_hours: "08:00-22:00",
      },
      destinations,
    );
    expect(payload).toEqual({
      destination_id: "dest-1",
      name: "Cafe Chill",
      description: "A cafe.",
      latitude: "6.8667",
      longitude: "81.0466",
      cuisine_type: "International",
      avg_meal_cost: 2000,
      operating_hours: hoursTextToApi("08:00-22:00"),
    });
  });

  it("maps an API restaurant record back to form-friendly values", () => {
    const record = {
      id: "rest-1",
      destination_id: "dest-2",
      name: "The Empire Cafe",
      avg_meal_cost: "1300.00",
      operating_hours: { monday: "07:00-21:00" },
    };
    expect(mapRestaurantFromApi(record, destinations)).toEqual({
      ...record,
      destination: "Kandy",
      operating_hours: "07:00-21:00",
      avg_meal_cost: "1300",
    });
  });
});
