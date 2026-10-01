function ChoiceChip({ label, active, onClick }) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
        active
          ? "bg-accent-100 text-accent-700"
          : "border border-border bg-surface text-ink shadow-control"
      }`}
    >
      {active && (
        <span aria-hidden="true" className="font-bold">
          ✓
        </span>
      )}
      {label}
    </button>
  );
}

export default ChoiceChip;
