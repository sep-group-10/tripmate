import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

// Public auth endpoints never need a session refresh - a 401 from any
// of these is a real answer (wrong credentials, bad token, etc.), not
// an expired session, and retrying could refresh an unrelated session
// that happens to be logged in in the same browser.
const PUBLIC_AUTH_PATHS = [
  "/api/v1/auth/login",
  "/api/v1/auth/register",
  "/api/v1/auth/google",
  "/api/v1/auth/refresh",
  "/api/v1/auth/forgot-password",
  "/api/v1/auth/reset-password",
  "/api/v1/auth/verify-email",
  "/api/v1/auth/resend-verification",
];

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
    const isPublicAuthCall = PUBLIC_AUTH_PATHS.includes(error.config?.url);
    // True once this request was already retried, so it can't loop forever.
    const alreadyRetried = error.config?._retry;

    if (isUnauthorized && !isPublicAuthCall && !alreadyRetried) {
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
