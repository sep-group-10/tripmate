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

export function listFeedback({ status, q } = {}) {
  return api
    .get("/api/v1/admin/feedback", { params: { status, q } })
    .then((res) => res.data.data);
}

export function resolveFeedback(id, { outcome, note }) {
  return api
    .patch(`/api/v1/admin/feedback/${id}/resolve`, { outcome, note })
    .then((res) => res.data.data);
}

export function reopenFeedback(id) {
  return api
    .patch(`/api/v1/admin/feedback/${id}/reopen`)
    .then((res) => res.data.data);
}

export function deleteFeedback(id) {
  return api
    .delete(`/api/v1/admin/feedback/${id}`)
    .then((res) => res.data.data);
}
