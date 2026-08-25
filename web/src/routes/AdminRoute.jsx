import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const ADMIN_ROLES = ["ADMIN", "SUPER_ADMIN"];

/** Guards /admin/* — requires both login AND an admin-capable role.
 * SUPER_ADMIN inherits ADMIN access; ADMIN does not inherit TOURIST (see
 * backend/app/core/roles.py), so this is an explicit allow-list, not a
 * numeric rank check. A logged-out user is sent to /login same as
 * ProtectedRoute; a logged-in Tourist is sent to / instead — redirecting
 * them to /login would be confusing since they're already logged in, just
 * not authorized for this section. */
function AdminRoute({ children }) {
  const { isAuthenticated, role } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!ADMIN_ROLES.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default AdminRoute;
