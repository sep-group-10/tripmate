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

export function listAdmins({ page = 1, limit = 20, q } = {}) {
  return api
    .get("/api/v1/admin/admins", { params: { page, limit, q } })
    .then((res) => res.data.data);
}

export function createAdmin(payload) {
  return api.post("/api/v1/admin/admins", payload).then((res) => res.data.data);
}

export function updateAdminStatus(adminId, isActive) {
  return api
    .patch(`/api/v1/admin/admins/${adminId}/status`, { is_active: isActive })
    .then((res) => res.data.data);
}
