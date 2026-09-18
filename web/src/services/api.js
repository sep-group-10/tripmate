import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

// Shared so concurrent 401s reuse one refresh call instead of racing.
let refreshPromise = null;

function refreshAccessToken() {
  if (refreshPromise === null) {
    refreshPromise = api.post("/api/v1/auth/refresh").finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const isUnauthorized = error.response?.status === 401;
    const isRefreshCall = error.config?.url === "/api/v1/auth/refresh";
    // True once this request was already retried, so it can't loop forever.
    const alreadyRetried = error.config?._retry;

    if (isUnauthorized && !isRefreshCall && !alreadyRetried) {
      try {
        await refreshAccessToken();
        error.config._retry = true;
        return api(error.config);
      } catch (refreshError) {
        // Refresh failed too - reject normally so the caller can log out.
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default api;
