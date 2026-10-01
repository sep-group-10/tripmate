import { describe, it, expect } from "vitest";
import { TRIP_STATUS } from "../constants/tripStatus";
import {
  InvalidTripStatusError,
  canSaveTrip,
  statusAfterSave,
  statusAfterUnsave,
} from "./tripStatus";

describe("trip status rules", () => {
  it("only a GENERATED trip can be saved", () => {
    expect(canSaveTrip(TRIP_STATUS.GENERATED)).toBe(true);
    expect(canSaveTrip(TRIP_STATUS.DRAFT)).toBe(false);
    expect(canSaveTrip(TRIP_STATUS.SAVED)).toBe(false);
  });

  it("saving moves GENERATED to SAVED", () => {
    expect(statusAfterSave(TRIP_STATUS.GENERATED)).toBe(TRIP_STATUS.SAVED);
  });

  it("rejects saving a DRAFT trip", () => {
    expect(() => statusAfterSave(TRIP_STATUS.DRAFT)).toThrow(
      InvalidTripStatusError,
    );
  });

  it("rejects saving a trip that is already SAVED", () => {
    expect(() => statusAfterSave(TRIP_STATUS.SAVED)).toThrow(
      InvalidTripStatusError,
    );
  });

  it("unsaving moves SAVED back to GENERATED", () => {
    expect(statusAfterUnsave(TRIP_STATUS.SAVED)).toBe(TRIP_STATUS.GENERATED);
  });

  it("rejects unsaving a trip that is not SAVED", () => {
    expect(() => statusAfterUnsave(TRIP_STATUS.GENERATED)).toThrow(
      InvalidTripStatusError,
    );
    expect(() => statusAfterUnsave(TRIP_STATUS.DRAFT)).toThrow(
      InvalidTripStatusError,
    );
  });
});
