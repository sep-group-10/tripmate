import { formatMoney } from "../../utils/tripFormat";
import SectionLabel from "./SectionLabel";
import TripHero from "./TripHero";

// Segment and dot color per budget category key.
const CATEGORY_COLORS = {
  accommodation: "bg-accent",
  dining: "bg-info",
  transport: "bg-warn",
  attractions: "bg-accent-300",
  misc: "bg-muted-400",
};

function BudgetTab({ summary, budget }) {
  // Percentages come from the amounts, so they always match the bar.
  const sum = budget.categories.reduce((n, category) => n + category.amount, 0);
  const rows = budget.categories.map((category) => ({
    ...category,
    color: CATEGORY_COLORS[category.key] ?? "bg-muted-400",
    share: sum > 0 ? (category.amount / sum) * 100 : 0,
  }));

  return (
    <>
      <TripHero summary={summary} />

      {/* Wraps instead of overflowing, and the bar below is a separate block,
          so a long total can never overlap it. */}
      <div className="flex flex-none flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <SectionLabel>Total planned spend</SectionLabel>
        <span className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
          <span className="font-heading text-[26px] leading-tight font-semibold tracking-[-0.03em] text-accent tabular-nums">
            {formatMoney(budget.total, budget.currency)}
          </span>
          <span className="text-helper text-muted-500 tabular-nums">
            {budget.per_day.toLocaleString("en-US")} / day
          </span>
        </span>
      </div>

      <div
        className="flex h-2.5 flex-none overflow-hidden rounded-pill bg-inset"
        role="img"
        aria-label="Spend by category"
      >
        {rows.map((row) => (
          <span
            key={row.key}
            className={`h-full ${row.color}`}
            style={{ width: `${row.share}%` }}
          />
        ))}
      </div>

      <div className="flex flex-none flex-col">
        {rows.map((row) => (
          <div
            key={row.key}
            className="flex items-center gap-2.5 border-t border-divider py-2.75"
          >
            <span className={`h-2 w-2 flex-none rounded-full ${row.color}`} />
            <span className="flex-1 text-body-sm text-muted-700">
              {row.label}
            </span>
            <span className="text-helper text-muted-500 tabular-nums">
              {Math.round(row.share)}%
            </span>
            <span className="min-w-22 text-right text-body-sm font-medium tabular-nums">
              {formatMoney(row.amount, budget.currency)}
            </span>
          </div>
        ))}
      </div>
    </>
  );
}

export default BudgetTab;
