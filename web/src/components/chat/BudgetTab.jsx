import { ITINERARY_DAYS } from "../../data/tripPlanDummyData";
import { BUDGET_CATEGORIES, computeBudget } from "../../utils/tripBudget";
import { formatMoney } from "../../utils/tripFormat";
import SectionLabel from "./SectionLabel";

function BudgetTab() {
  const { amounts, total } = computeBudget();
  const rows = BUDGET_CATEGORIES.map((category) => ({
    ...category,
    amount: amounts[category.key],
    percent: total ? Math.round((amounts[category.key] / total) * 100) : 0,
  }));

  return (
    <>
      <div className="flex flex-none items-baseline justify-between gap-3">
        <SectionLabel>Total planned spend</SectionLabel>
        <span className="flex items-baseline gap-2">
          <span className="font-heading text-[26px] font-semibold tracking-tight text-accent">
            {formatMoney(total)}
          </span>
          <span className="text-helper text-muted-500">
            {formatMoney(Math.round(total / ITINERARY_DAYS.length))} / day
          </span>
        </span>
      </div>

      <div
        className="flex h-2.5 flex-none overflow-hidden rounded-pill bg-inset"
        role="img"
        aria-label="Spend by category"
      >
        {rows
          .filter((row) => row.amount > 0)
          .map((row) => (
            <span
              key={row.key}
              className={`h-full ${row.color}`}
              style={{ width: `${row.percent}%` }}
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
            <span className="text-helper text-muted-500">
              {row.amount > 0 ? `${row.percent}%` : "—"}
            </span>
            <span
              className={`min-w-22 text-right text-body-sm font-medium ${row.amount > 0 ? "" : "text-muted-500"}`}
            >
              {formatMoney(row.amount, "LKR 0")}
            </span>
          </div>
        ))}
      </div>
    </>
  );
}

export default BudgetTab;
