import { CircleAlert } from "lucide-react";

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
      <label htmlFor={id} className="mb-1.5 block text-label text-muted-700">
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
          <CircleAlert size={14} aria-hidden="true" />
          {error}
        </span>
      )}
    </div>
  );
}

export default FormInput;
