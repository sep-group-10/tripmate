import { NavLink, Outlet, Link } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/destinations", label: "Destinations" },
  { to: "/admin/attractions", label: "Attractions" },
  { to: "/admin/hotels", label: "Hotels" },
  { to: "/admin/restaurants", label: "Restaurants" },
];

function AdminLayout() {
  return (
    <div className="font-body grid min-h-screen grid-cols-[232px_minmax(0,1fr)] bg-bg text-ink">
      <aside className="sticky top-0 flex h-screen flex-col gap-6 p-4">
        <div className="flex items-center gap-2.5 px-2">
          <span className="flex h-[26px] w-[26px] items-center justify-center rounded-lg bg-accent text-white">
            <svg
              width="15"
              height="15"
              viewBox="0 0 256 256"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.41,134.55a8,8,0,0,0,9.18,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Zm0,56a32,32,0,1,1-32,32A32,32,0,0,1,128,72Z" />
            </svg>
          </span>
          <span className="font-heading text-[15px] font-semibold tracking-tight">
            TripMate
          </span>
          <span className="ml-auto rounded-[6px] bg-muted-300 px-2 py-[3px] font-mono text-[10px] font-medium tracking-wider text-muted-700 uppercase">
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
                `rounded-pill px-3 py-2 text-left text-[13.5px] ${
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
          <Link to="/" className="text-left text-[13px] text-muted-700">
            Exit admin
          </Link>
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 flex-none items-center justify-center rounded-pill bg-accent-100 text-xs font-semibold text-accent-700">
              SA
            </span>
            <div className="flex flex-col">
              <span className="text-[13.5px] font-medium">Super Admin</span>
              <span className="text-[11.5px] text-muted-600">
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
