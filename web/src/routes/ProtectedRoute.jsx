import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  // Wait for AuthContext's initial GET /users/me session-restore check
  // before deciding - otherwise a logged-in user hitting this route on a
  // fresh page load gets bounced to /login before that check resolves.
  if (loading) return null;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
