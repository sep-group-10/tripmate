export function formatDate(iso) {
  const date = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(date.getTime())) return String(iso ?? "");
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function formatMoney(amount, freeLabel = "Free") {
  return amount === 0 ? freeLabel : `LKR ${amount.toLocaleString("en-US")}`;
}
