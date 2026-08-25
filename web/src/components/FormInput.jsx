function FormInput({
  id,
  label,
  error,
  endAdornment,
  className = "",
  as = "input",
  ...inputProps
}) {
  const Tag = as;
  return (
    <div className={className}>
      <label htmlFor={id} className="mb-1.5 block text-[13px] text-muted-700">
        {label}
      </label>
      <div className="relative flex">
        <Tag
          id={id}
          className={`min-h-10 w-full flex-1 rounded-lg border bg-surface px-3 py-2.5 text-sm text-ink shadow-inset outline-none ${endAdornment ? "pr-11" : ""} ${error ? "border-danger" : "border-border"} ${as === "textarea" ? "resize-y" : ""}`}
          aria-invalid={Boolean(error)}
          {...inputProps}
        />
        {endAdornment}
      </div>
      {error && (
        <span className="mt-1.5 flex items-center gap-1.5 text-xs text-danger">
          <svg
            width="14"
            height="14"
            viewBox="0 0 256 256"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M128,24A104,104,0,1,0,232,128A104.11,104.11,0,0,0,128,24Zm-8,56a8,8,0,0,1,16,0v56a8,8,0,0,1-16,0Zm8,104a12,12,0,1,1,12-12A12,12,0,0,1,128,184Z" />
          </svg>
          {error}
        </span>
      )}
    </div>
  );
}

export default FormInput;
