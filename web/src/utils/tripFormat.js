export function formatDate(iso) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export function formatMoney(amount, freeLabel = "Free") {
  return amount === 0 ? freeLabel : `LKR ${amount.toLocaleString("en-US")}`;
}

export function formatDuration(minutes) {
  if (minutes < 60) return `${minutes} min`;
  const rest = minutes % 60;
  return `${Math.floor(minutes / 60)} h${rest ? ` ${rest} min` : ""}`;
}
