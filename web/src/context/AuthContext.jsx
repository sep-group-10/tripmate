import { useEffect, useState } from "react";
import { AuthContext } from "./authContext";
import api from "../services/api";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  // Mirrors the backend's role field (backend/app/core/roles.py): "TOURIST"
  // | "ADMIN" | "SUPER_ADMIN".
  const [role, setRole] = useState(null);
  // True until the initial session-restore check below settles. The
  // access-token cookie survives a page refresh but this React state does
  // not, so route guards (ProtectedRoute/AdminRoute) must wait for this
  // instead of assuming "logged out" while the check is still in flight.
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .get("/api/v1/users/me")
      .then((response) => {
        if (cancelled) return;
        const me = response.data.data;
        setUser(me);
        setRole(me.role);
        setIsAuthenticated(true);
      })
      .catch(() => {
        // No valid session (never logged in, or the cookie is missing or
        // expired) - an expected outcome on a fresh visit, not an error.
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Sets the active session from a user object returned by a successful
  // /auth/register or /auth/login call - also reused after a profile save
  // to refresh the cached user without a second round trip.
  const login = (userData) => {
    setUser(userData);
    setRole(userData.role);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } catch {
      // Best-effort: clear local state below regardless, so the UI always
      // reflects "logged out" even if the request itself failed.
    }
    setUser(null);
    setRole(null);
    setIsAuthenticated(false);
  };

  // KNOWN LIMITATION (C4.1): there is no POST /auth/refresh endpoint yet
  // (backend/app/routers/auth.py only has register/login/logout), so an
  // access token that comes back TOKEN_EXPIRED or UNAUTHORIZED can't be
  // silently renewed. Callers should treat that as a full session expiry -
  // call clearSession() and let ProtectedRoute/AdminRoute redirect to
  // /login - rather than attempting to refresh. Revisit once the refresh
  // token feature (docs/auth-flow.md) actually lands.
  const clearSession = () => {
    setUser(null);
    setRole(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        role,
        loading,
        login,
        logout,
        clearSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
