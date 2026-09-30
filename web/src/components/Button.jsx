const VARIANT_CLASSES = {
  primary:
    "bg-accent text-white shadow-control hover:bg-accent-600 active:bg-accent-700",
  dark: "bg-muted-900 text-white shadow-control",
  outline: "border border-border bg-surface text-ink shadow-control",
  danger: "bg-danger text-white shadow-control hover:opacity-90",
  dangerOutline: "border border-danger text-danger shadow-control",
  ghost: "text-muted-700",
};

function Button({
  variant = "primary",
  className = "",
  disabled,
  children,
  ...props
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      className={`rounded-full px-5 py-2.5 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-70 ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
