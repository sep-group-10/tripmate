function ToggleSwitch({ checked, onChange, label, description }) {
  return (
    <div className="flex items-center justify-between gap-6">
      {(label || description) && (
        <div>
          {label && <div className="text-sm font-medium">{label}</div>}
          {description && (
            <div className="text-helper text-muted-600">{description}</div>
          )}
        </div>
      )}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={onChange}
        className={`relative h-[22px] w-[38px] flex-none rounded-pill transition-colors ${
          checked ? "bg-accent" : "bg-muted-400"
        }`}
      >
        <span
          className={`absolute top-[3px] h-4 w-4 rounded-full bg-white shadow-control transition-transform ${
            checked ? "translate-x-[19px]" : "translate-x-[3px]"
          }`}
        />
      </button>
    </div>
  );
}

export default ToggleSwitch;
