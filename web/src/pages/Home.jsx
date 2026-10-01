import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ADMIN_ROLES } from "../constants/roles";
import FullPageLoader from "../components/FullPageLoader";

function Home() {
  const { isAuthenticated, loading, role } = useAuth();

  if (loading) return <FullPageLoader />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (ADMIN_ROLES.includes(role)) return <Navigate to="/admin" replace />;

  return <Navigate to="/chat" replace />;
}

export default Home;
