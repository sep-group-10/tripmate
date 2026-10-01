import { Link } from "react-router-dom";
import KpiCard from "../../components/KpiCard";
import TrendChart from "../../components/TrendChart";
import ActivityList from "../../components/ActivityList";
import BarMeterList from "../../components/BarMeterList";
import { useTourismData } from "../../hooks/useTourismData";

// TODO(backend): replace with GET /api/v1/admin/stats once it exists.
const KPIS = [
  { label: "Draft trips", value: "428", note: "Currently in progress" },
  { label: "Destinations", value: "20", note: "Active in AI planner" },
  {
    label: "Total users",
    value: "3,284",
    note: "+47 this week",
    accent: true,
  },
  { label: "Pending feedback", value: "4", note: "Awaiting review" },
];

// TODO(backend): replace with GET /api/v1/admin/trips-growth once it exists.
const TRIPS_GROWTH = [
  { month: "Sep", trips: 210, users: 140 },
  { month: "Oct", trips: 232, users: 158 },
  { month: "Nov", trips: 224, users: 150 },
  { month: "Dec", trips: 268, users: 168 },
  { month: "Jan", trips: 258, users: 162 },
  { month: "Feb", trips: 302, users: 184 },
  { month: "Mar", trips: 294, users: 180 },
  { month: "Apr", trips: 320, users: 198 },
  { month: "May", trips: 312, users: 206 },
  { month: "Jun", trips: 350, users: 214 },
  { month: "Jul", trips: 344, users: 220 },
  { month: "Aug", trips: 382, users: 232 },
];

// TODO(backend): replace with GET /api/v1/admin/feedback-and-activity (or
// equivalent) once a real activity source exists - these rows are illustrative.
const RECENT_ACTIVITY = [
  {
    kind: "User",
    title: "Arjun Krishnamurthy registered",
    meta: "arjun.k@gmail.com",
    time: "4 min ago",
  },
  {
    kind: "Pricing",
    title: "Sigiriya Rock Fortress entry fee updated",
    meta: "USD 30 (was USD 25)",
    time: "31 min ago",
  },
  {
    kind: "Feedback",
    title: "Feedback submitted — 5 stars",
    meta: "Nimal Perera · Ella trip",
    time: "2 hr ago",
  },
];

const RANGES = ["30 d", "6 mo", "12 mo"];

function AdminDashboard() {
  const { destinations, destinationsTotal } = useTourismData();

  // TODO(backend): "trips per destination" isn't tracked yet - standing in
  // with the destinations already loaded, ranked by rating instead.
  const popularDestinations = destinations.slice(0, 5).map((d) => {
    const rating = Number(d.rating) || 0;
    return {
      id: d.id,
      label: d.name,
      note: rating ? `${rating.toFixed(1)} ★` : "No rating",
      pct: Math.round((rating / 5) * 100),
    };
  });

  return (
    <div className="flex flex-col gap-4">
      <header className="flex flex-wrap items-center justify-between gap-6">
        <h1 className="font-heading text-heading-md font-semibold tracking-tight text-ink">
          Dashboard
        </h1>
        <div className="flex items-center gap-2.5">
          <input
            type="text"
            placeholder="Quick search…"
            aria-label="Search"
            className="w-search rounded-pill border border-border bg-surface px-3.5 py-2.5 text-body-sm shadow-control outline-none placeholder:text-muted-500 focus:border-accent"
          />
          <span className="inline-flex gap-0.5 rounded-pill bg-muted-300 p-0.75">
            {RANGES.map((label) => (
              <button
                key={label}
                type="button"
                className={`rounded-pill px-3.5 py-1.5 text-label font-medium ${
                  label === "12 mo"
                    ? "bg-surface text-ink shadow-control"
                    : "text-muted-700"
                }`}
              >
                {label}
              </button>
            ))}
          </span>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {KPIS.map((kpi) => (
          <KpiCard key={kpi.label} {...kpi} />
        ))}
      </div>

      <section className="flex flex-col gap-4 rounded-card bg-surface p-6 shadow-control">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <h2 className="font-heading text-md font-semibold text-ink">
              Trips generated vs. new users
            </h2>
            <p className="mt-1 text-label text-muted-600">
              Rolling 12 mo · updated 4 minutes ago
            </p>
          </div>
          <div className="flex gap-4 text-label text-muted-700">
            <span className="flex items-center gap-1.5">
              <span className="h-0.5 w-3.5 rounded-full bg-accent" />
              Trips generated
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-0.5 w-3.5 rounded-full bg-info" />
              New users
            </span>
          </div>
        </div>

        <TrendChart
          data={TRIPS_GROWTH}
          xKey="month"
          primaryKey="trips"
          secondaryKey="users"
          height={240}
        />
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="flex min-w-0 flex-col gap-4">
          <section className="overflow-hidden rounded-card bg-surface shadow-control">
            <div className="flex items-center justify-between border-b border-divider px-7 py-4.5">
              <h2 className="font-heading text-md font-semibold text-ink">
                Recent activity
              </h2>
              <Link to="#" className="text-label text-accent hover:underline">
                View all
              </Link>
            </div>
            <ActivityList items={RECENT_ACTIVITY} />
          </section>
        </div>

        <div className="flex flex-col gap-4">
          <section className="flex flex-col gap-3 rounded-card bg-surface p-5.5 shadow-control">
            <h2 className="font-heading text-md font-semibold text-ink">
              Quick actions
            </h2>
            <Link
              to="/admin/destinations"
              className="rounded-pill bg-accent px-4 py-2.5 text-center text-body-sm font-medium text-white shadow-control hover:bg-accent-600"
            >
              Add destination
            </Link>
            <Link
              to="/admin/admins"
              className="rounded-pill border border-border bg-surface px-4 py-2.5 text-center text-body-sm font-medium text-ink shadow-control hover:border-muted-400"
            >
              Manage admins
            </Link>
            <Link
              to="/admin/feedback"
              className="rounded-pill border border-border bg-surface px-4 py-2.5 text-center text-body-sm font-medium text-ink shadow-control hover:border-muted-400"
            >
              Review feedback
            </Link>
          </section>

          <section className="flex flex-col gap-3.5 rounded-card bg-surface p-5.5 shadow-control">
            <h2 className="font-heading text-md font-semibold text-ink">
              Popular destinations
            </h2>
            <BarMeterList
              items={popularDestinations}
              emptyLabel="No destinations yet."
            />
            <p className="text-helper text-muted-500">
              Ranked by rating · {destinationsTotal || destinations.length}{" "}
              destinations total
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
