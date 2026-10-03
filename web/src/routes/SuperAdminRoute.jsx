import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import FullPageLoader from "../components/FullPageLoader";
import { SUPER_ADMIN_ROLES } from "../constants/roles";

/** Guards super-admin-only pages nested under /admin/* (e.g. managing
 * other admin accounts). Assumes AdminRoute already confirmed the user
 * is logged in and admin-capable, so a plain ADMIN here is sent back to
 * /admin rather than /login. */
function SuperAdminRoute({ children }) {
  const { role, loading } = useAuth();

  if (loading) return <FullPageLoader />;

  if (!SUPER_ADMIN_ROLES.includes(role)) {
    return <Navigate to="/admin" replace />;
  }

  return children;
}

export default SuperAdminRoute;
