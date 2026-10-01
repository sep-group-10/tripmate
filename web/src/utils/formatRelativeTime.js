const UNITS = [
  { limit: 60, divisor: 1, label: "sec" },
  { limit: 3600, divisor: 60, label: "min" },
  { limit: 86400, divisor: 3600, label: "hr" },
  { limit: 2592000, divisor: 86400, label: "day" },
];

/** Formats an ISO timestamp as a short relative string ("4 min ago",
 * "2 hr ago"), falling back to a plain date once it's over 30 days old. */
export function formatRelativeTime(isoString) {
  const then = new Date(isoString).getTime();
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000));

  if (seconds < 5) return "just now";

  for (const { limit, divisor, label } of UNITS) {
    if (seconds < limit) {
      const value = Math.max(1, Math.floor(seconds / divisor));
      return `${value} ${label}${value === 1 ? "" : "s"} ago`;
    }
  }

  return new Date(isoString).toLocaleDateString();
}
