import { describe, it, expect } from "vitest";
import { TRIP_STATUS } from "../constants/tripStatus";
import { MY_TRIPS } from "../data/myTripsDummyData";
import { parseApiError } from "../utils/apiError";
import { createTripsService } from "./tripsService";

const seed = [
  { id: "d", title: "Draft trip", status: TRIP_STATUS.DRAFT },
  { id: "g", title: "Generated trip", status: TRIP_STATUS.GENERATED },
  { id: "s", title: "Saved trip", status: TRIP_STATUS.SAVED },
];

const statusOf = (service, id) =>
  service.listTrips().find((trip) => trip.id === id).status;

describe("mock trips data", () => {
  it("has a mix of all three statuses", () => {
    const statuses = new Set(MY_TRIPS.map((trip) => trip.status));
    expect(statuses).toEqual(
      new Set([TRIP_STATUS.DRAFT, TRIP_STATUS.GENERATED, TRIP_STATUS.SAVED]),
    );
  });
});

describe("saveTrip", () => {
  it("moves a GENERATED trip to SAVED and returns { success, data }", async () => {
    const service = createTripsService(seed);
    const response = await service.saveTrip("g");
    expect(response.success).toBe(true);
    expect(response.data).toMatchObject({ id: "g", status: TRIP_STATUS.SAVED });
    expect(statusOf(service, "g")).toBe(TRIP_STATUS.SAVED);
  });

  it("rejects a DRAFT trip and leaves it unchanged", async () => {
    const service = createTripsService(seed);
    await expect(service.saveTrip("d")).rejects.toMatchObject({
      response: {
        status: 400,
        data: { success: false, error: { code: "VALIDATION_ERROR" } },
      },
    });
    expect(statusOf(service, "d")).toBe(TRIP_STATUS.DRAFT);
  });

  it("rejects a trip that is already SAVED", async () => {
    const service = createTripsService(seed);
    await expect(service.saveTrip("s")).rejects.toMatchObject({
      response: { status: 400 },
    });
    expect(statusOf(service, "s")).toBe(TRIP_STATUS.SAVED);
  });

  it("rejects an unknown trip with NOT_FOUND", async () => {
    const service = createTripsService(seed);
    await expect(service.saveTrip("nope")).rejects.toMatchObject({
      response: { status: 404, data: { error: { code: "NOT_FOUND" } } },
    });
  });

  it("produces errors that parseApiError understands", async () => {
    const service = createTripsService(seed);
    const error = await service.saveTrip("d").catch((caught) => caught);
    expect(parseApiError(error)).toMatchObject({
      code: "VALIDATION_ERROR",
      message: "Only generated trips can be saved.",
    });
  });
});

describe("unsaveTrip", () => {
  it("moves a SAVED trip back to GENERATED", async () => {
    const service = createTripsService(seed);
    const response = await service.unsaveTrip("s");
    expect(response.success).toBe(true);
    expect(response.data.status).toBe(TRIP_STATUS.GENERATED);
    expect(statusOf(service, "s")).toBe(TRIP_STATUS.GENERATED);
  });

  it("rejects trips that are not SAVED", async () => {
    const service = createTripsService(seed);
    await expect(service.unsaveTrip("g")).rejects.toMatchObject({
      response: { status: 400 },
    });
    await expect(service.unsaveTrip("d")).rejects.toMatchObject({
      response: { status: 400 },
    });
  });

  it("a trip can be saved, removed and saved again", async () => {
    const service = createTripsService(seed);
    await service.saveTrip("g");
    await service.unsaveTrip("g");
    expect(statusOf(service, "g")).toBe(TRIP_STATUS.GENERATED);
    await service.saveTrip("g");
    expect(statusOf(service, "g")).toBe(TRIP_STATUS.SAVED);
  });
});

describe("listTrips", () => {
  it("returns copies, so callers can't change the store", () => {
    const service = createTripsService(seed);
    service.listTrips()[0].status = TRIP_STATUS.SAVED;
    expect(statusOf(service, "d")).toBe(TRIP_STATUS.DRAFT);
  });
});
