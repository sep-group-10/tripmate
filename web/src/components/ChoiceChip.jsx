function ChoiceChip({ label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-3.5 py-1.5 text-xs font-medium ${
        active
          ? "bg-accent-100 text-accent-700"
          : "border border-border bg-surface text-ink shadow-control"
      }`}
    >
      {label}
    </button>
  );
}

export default ChoiceChip;
