import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import KpiCard from "../../components/KpiCard";
import TrendChart from "../../components/TrendChart";
import ActivityList from "../../components/ActivityList";
import BarMeterList from "../../components/BarMeterList";
import { useTourismData } from "../../hooks/useTourismData";
import {
  getAdminStats,
  getTripsGrowth,
  getRecentActivity,
} from "../../services/adminApi";
import { formatRelativeTime } from "../../utils/formatRelativeTime";

const RANGES = ["30 d", "6 mo", "12 mo"];

function AdminDashboard() {
  const { destinations, destinationsTotal } = useTourismData();

  const [stats, setStats] = useState(null);
  const [statsStatus, setStatsStatus] = useState("loading");
  const [tripsGrowth, setTripsGrowth] = useState([]);
  const [tripsGrowthStatus, setTripsGrowthStatus] = useState("loading");
  const [activity, setActivity] = useState([]);
  const [activityStatus, setActivityStatus] = useState("loading");

  useEffect(() => {
    let cancelled = false;
    getAdminStats()
      .then((data) => {
        if (cancelled) return;
        setStats(data);
        setStatsStatus("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setStatsStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    getTripsGrowth()
      .then((data) => {
        if (cancelled) return;
        setTripsGrowth(
          data.months.map((m) => ({
            month: m.label,
            trips: m.trips,
            users: m.users,
          })),
        );
        setTripsGrowthStatus("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setTripsGrowthStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    getRecentActivity(6)
      .then((data) => {
        if (cancelled) return;
        setActivity(
          data.map((entry) => ({
            kind: entry.kind,
            title: entry.title,
            meta: entry.meta ?? "",
            time: formatRelativeTime(entry.created_at),
          })),
        );
        setActivityStatus("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setActivityStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const kpis = [
    {
      label: "Draft trips",
      value: statsStatus === "ready" ? stats.draft_trips_count : "—",
      note: "Currently in progress",
    },
    {
      label: "Destinations",
      value: statsStatus === "ready" ? stats.destinations_count : "—",
      note: "Active in AI planner",
    },
    {
      label: "Total users",
      value: statsStatus === "ready" ? stats.total_users : "—",
      note: statsStatus === "error" ? "Couldn't load" : "Registered accounts",
      accent: true,
    },
    {
      label: "Pending feedback",
      value: statsStatus === "ready" ? stats.pending_feedback_count : "—",
      note: "Awaiting review",
    },
  ];

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
        {kpis.map((kpi) => (
          <KpiCard key={kpi.label} {...kpi} />
        ))}
      </div>

      <section className="flex flex-col gap-4 rounded-card bg-surface p-6 shadow-control">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <h2 className="font-heading text-md font-semibold text-ink">
              Trips generated vs. new users
            </h2>
            <p className="mt-1 text-label text-muted-600">Rolling 12 mo</p>
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

        {tripsGrowthStatus === "error" ? (
          <p className="py-8 text-center text-body-sm text-muted-600">
            Couldn't load trend data.
          </p>
        ) : (
          <TrendChart
            data={tripsGrowth}
            xKey="month"
            primaryKey="trips"
            secondaryKey="users"
            height={240}
          />
        )}
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="flex min-w-0 flex-col gap-4">
          <section className="overflow-hidden rounded-card bg-surface shadow-control">
            <div className="flex items-center justify-between border-b border-divider px-7 py-4.5">
              <h2 className="font-heading text-md font-semibold text-ink">
                Recent activity
              </h2>
            </div>
            {activityStatus === "error" ? (
              <p className="px-7 py-8 text-center text-body-sm text-muted-600">
                Couldn't load recent activity.
              </p>
            ) : activityStatus === "ready" && activity.length === 0 ? (
              <p className="px-7 py-8 text-center text-body-sm text-muted-600">
                No activity yet.
              </p>
            ) : (
              <ActivityList items={activity} />
            )}
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
