import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ADMIN_ROLES } from "../constants/roles";
import FullPageLoader from "../components/FullPageLoader";

function NotFoundPage() {
  const { isAuthenticated, loading, role } = useAuth();
  const navigate = useNavigate();

  if (loading) return <FullPageLoader />;

  const homePath = !isAuthenticated
    ? "/"
    : ADMIN_ROLES.includes(role)
      ? "/admin"
      : "/profile";

  return (
    <main className="font-body flex min-h-screen flex-col items-center justify-center gap-4 bg-bg px-6 text-center text-ink">
      <p className="m-0 font-mono text-sm font-medium tracking-widest text-muted-600">
        404
      </p>
      <h1 className="font-heading m-0 text-heading-md font-semibold tracking-tight">
        Page not found
      </h1>
      <p className="m-0 max-w-md text-sm text-muted-600">
        We couldn’t find the page you’re looking for.
      </p>
      <button
        type="button"
        onClick={() => navigate(homePath, { replace: true })}
        className="mt-2 rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
      >
        Go home
      </button>
    </main>
  );
}

export default NotFoundPage;
