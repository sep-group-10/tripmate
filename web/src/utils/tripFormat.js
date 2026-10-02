const parse = (iso) => new Date(`${iso}T00:00:00`);

export function formatDate(iso) {
  const date = parse(iso);
  if (Number.isNaN(date.getTime())) return String(iso ?? "");
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// "Sep 12–18" (same month) or "Sep 28 – Oct 4"; withYear appends ", 2026".
export function formatDateRange(startIso, endIso, { withYear = false } = {}) {
  const start = parse(startIso);
  const end = parse(endIso);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    return `${startIso ?? ""} – ${endIso ?? ""}`;
  }
  const sameMonth =
    start.getMonth() === end.getMonth() &&
    start.getFullYear() === end.getFullYear();
  const range = sameMonth
    ? `${formatDate(startIso)}–${end.getDate()}`
    : `${formatDate(startIso)} – ${formatDate(endIso)}`;
  return withYear ? `${range}, ${end.getFullYear()}` : range;
}

// Inclusive number of days between two ISO dates (Sep 12 to Sep 18 is 7).
export function tripDurationDays(startIso, endIso) {
  const ms = parse(endIso) - parse(startIso);
  return Number.isNaN(ms) ? 0 : Math.round(ms / 86400000) + 1;
}

export function formatMoney(amount, currency = "LKR") {
  return `${currency} ${amount.toLocaleString("en-US")}`;
}
