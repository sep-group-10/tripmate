import { NavLink, Outlet, Link, useNavigate } from "react-router-dom";
import { MapPin } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/destinations", label: "Destinations" },
  { to: "/admin/attractions", label: "Attractions" },
  { to: "/admin/hotels", label: "Hotels" },
  { to: "/admin/restaurants", label: "Restaurants" },
];

function AdminLayout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="font-body grid min-h-screen grid-cols-[232px_minmax(0,1fr)] bg-bg text-ink">
      <aside className="sticky top-0 flex h-screen flex-col gap-6 p-4">
        <div className="flex items-center gap-2.5 px-2">
          <span className="flex h-logo w-logo items-center justify-center rounded-lg bg-accent text-white">
            <MapPin size={15} aria-hidden="true" />
          </span>
          <span className="font-heading text-md font-semibold tracking-tight">
            TripMate
          </span>
          <span className="ml-auto rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
            Admin
          </span>
        </div>

        <nav className="flex flex-col gap-0.5">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `rounded-pill px-3 py-2 text-left text-body-sm ${
                  isActive
                    ? "bg-surface font-medium text-ink shadow-control"
                    : "text-muted-700"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto flex flex-col gap-3 border-t border-divider px-2 pt-4">
          <div className="flex items-center justify-between gap-3">
            <Link to="/" className="text-left text-label text-muted-700">
              Exit admin
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="text-left text-label text-muted-700"
            >
              Log out
            </button>
          </div>
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 flex-none items-center justify-center rounded-pill bg-accent-100 text-xs font-semibold text-accent-700">
              SA
            </span>
            <div className="flex flex-col">
              <span className="text-body-sm font-medium">Super Admin</span>
              <span className="text-caption text-muted-600">
                admin@tripmate.lk
              </span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex min-w-0 flex-col gap-4 px-6 py-5 pb-16">
        <Outlet />
      </main>
    </div>
  );
}

export default AdminLayout;
