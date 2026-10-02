import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { MapPin } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { ADMIN_ROLES } from "../constants/roles";

const NAV_ITEMS = [
  { to: "/chat", label: "Chat" },
  { to: "/trips", label: "My trips" },
  { to: "/profile", label: "Profile" },
];

function initials(name) {
  const trimmed = (name ?? "").trim();
  if (!trimmed) return "?";
  return trimmed
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

function UserLayout() {
  const { logout, user, role } = useAuth();
  const navigate = useNavigate();
  const displayName = user?.full_name?.trim() || "Traveller";
  const displayEmail = user?.email?.trim() || "—";

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="font-body grid h-screen grid-cols-[232px_minmax(0,1fr)] bg-bg text-ink">
      <aside className="flex h-screen flex-col gap-6 p-4">
        <div className="flex items-center gap-2.5 px-2">
          <span className="flex h-logo w-logo items-center justify-center rounded-lg bg-accent text-white">
            <MapPin size={15} aria-hidden="true" />
          </span>
          <span className="font-heading text-md font-semibold tracking-tight">
            TripMate
          </span>
        </div>

        <nav className="flex flex-col gap-0.5">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
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
          {ADMIN_ROLES.includes(role) && (
            <NavLink
              to="/admin"
              className="text-left text-label text-muted-700"
            >
              Admin
            </NavLink>
          )}
          <button
            type="button"
            onClick={handleLogout}
            className="text-left text-label text-muted-700"
          >
            Log out
          </button>
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 flex-none items-center justify-center rounded-pill bg-accent-100 text-xs font-semibold text-accent-700">
              {initials(user?.full_name)}
            </span>
            <div className="flex flex-col">
              <span className="text-body-sm font-medium">{displayName}</span>
              <span className="text-caption text-muted-600">
                {displayEmail}
              </span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex min-h-0 min-w-0 flex-col overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

export default UserLayout;
