import api from "./api";

export function getAdminStats() {
  return api.get("/api/v1/admin/stats").then((res) => res.data.data);
}

export function getTripsGrowth() {
  return api.get("/api/v1/admin/trips-growth").then((res) => res.data.data);
}

export function getRecentActivity(limit = 6) {
  return api
    .get("/api/v1/admin/activity", { params: { limit } })
    .then((res) => res.data.data);
}
