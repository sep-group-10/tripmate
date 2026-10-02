import { describe, it, expect } from "vitest";
import { TRIP_STATUS } from "../constants/tripStatus";
import { MY_TRIPS } from "../data/myTripsDummyData";
import { TRIP_FILTERS, TRIP_SORTS, groupTrips } from "./tripFilters";

const ids = (trips) => trips.map((trip) => trip.id).sort();

describe("TRIP_FILTERS", () => {
  it("is All, Drafts, Generated, Saved in that order", () => {
    expect(TRIP_FILTERS).toEqual(["All", "Drafts", "Generated", "Saved"]);
  });
});

describe("groupTrips filter", () => {
  const count = (status) =>
    MY_TRIPS.filter((trip) => trip.status === status).length;

  it("All shows every trip, grouped by status", () => {
    const groups = groupTrips(MY_TRIPS, { filter: "All" });
    expect(groups.saved).toHaveLength(count(TRIP_STATUS.SAVED));
    expect(groups.generated).toHaveLength(count(TRIP_STATUS.GENERATED));
    expect(groups.drafts).toHaveLength(count(TRIP_STATUS.DRAFT));
    expect(groups.shownCount).toBe(MY_TRIPS.length);
  });

  it("Drafts shows only drafts", () => {
    const groups = groupTrips(MY_TRIPS, { filter: "Drafts" });
    expect(groups.drafts).toHaveLength(count(TRIP_STATUS.DRAFT));
    expect(groups.generated).toEqual([]);
    expect(groups.saved).toEqual([]);
    expect(groups.shownCount).toBe(count(TRIP_STATUS.DRAFT));
  });

  it("Generated shows only generated trips", () => {
    const groups = groupTrips(MY_TRIPS, { filter: "Generated" });
    expect(groups.generated).toHaveLength(count(TRIP_STATUS.GENERATED));
    expect(groups.drafts).toEqual([]);
    expect(groups.saved).toEqual([]);
    expect(groups.shownCount).toBe(count(TRIP_STATUS.GENERATED));
  });

  it("Saved shows only saved trips", () => {
    const groups = groupTrips(MY_TRIPS, { filter: "Saved" });
    expect(groups.saved).toHaveLength(count(TRIP_STATUS.SAVED));
    expect(groups.drafts).toEqual([]);
    expect(groups.generated).toEqual([]);
    expect(groups.shownCount).toBe(count(TRIP_STATUS.SAVED));
  });

  it("an empty section stays empty so the page can hide it", () => {
    const noSaved = MY_TRIPS.filter((t) => t.status !== TRIP_STATUS.SAVED);
    expect(groupTrips(noSaved, { filter: "All" }).saved).toEqual([]);
    expect(groupTrips(noSaved, { filter: "Saved" }).shownCount).toBe(0);
  });

  it("a trip moves between sections when its status changes", () => {
    const generated = MY_TRIPS.find((t) => t.status === TRIP_STATUS.GENERATED);
    const after = MY_TRIPS.map((trip) =>
      trip.id === generated.id ? { ...trip, status: TRIP_STATUS.SAVED } : trip,
    );
    const before = groupTrips(MY_TRIPS, { filter: "All" });
    const now = groupTrips(after, { filter: "All" });
    expect(ids(now.saved)).toContain(generated.id);
    expect(ids(now.generated)).not.toContain(generated.id);
    expect(now.saved).toHaveLength(before.saved.length + 1);
    expect(now.shownCount).toBe(before.shownCount);
  });
});

describe("groupTrips search and sort", () => {
  it("search matches title, place and a draft's prompt, within a filter", () => {
    expect(
      ids(groupTrips(MY_TRIPS, { filter: "All", query: "kandy" }).saved),
    ).toContain("saved-1");
    expect(
      groupTrips(MY_TRIPS, { filter: "Drafts", query: "elephants" }).drafts,
    ).toHaveLength(1);
    expect(
      groupTrips(MY_TRIPS, { filter: "Saved", query: "elephants" }).shownCount,
    ).toBe(0);
  });

  it("no match gives shownCount 0 (the page's empty state)", () => {
    expect(groupTrips(MY_TRIPS, { query: "zzz-no-such-trip" }).shownCount).toBe(
      0,
    );
  });

  it("sorts each section", () => {
    const { saved } = groupTrips(MY_TRIPS, {
      filter: "Saved",
      sort: TRIP_SORTS.Name,
    });
    const titles = saved.map((trip) => trip.title);
    expect(titles).toEqual([...titles].sort((a, b) => a.localeCompare(b)));
  });
});
