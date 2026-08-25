import { useState } from "react";
import { AuthContext } from "./authContext";

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  // Mirrors the backend's role field (backend/app/core/roles.py): "TOURIST"
  // | "ADMIN" | "SUPER_ADMIN". No real login yet (that's C4), so login()
  // accepts a mock role for testing route guards against each one.
  const [role, setRole] = useState(null);

  const login = (mockRole = "TOURIST") => {
    setIsAuthenticated(true);
    setRole(mockRole);
  };

  const logout = () => {
    setIsAuthenticated(false);
    setRole(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
