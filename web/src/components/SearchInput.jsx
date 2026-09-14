function SearchInput({ value, onChange, placeholder, className = "" }) {
  return (
    <input
      type="search"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      aria-label={placeholder}
      className={`min-h-10 rounded-pill border border-border bg-surface px-4 py-2 text-sm text-ink shadow-inset outline-none ${className}`}
    />
  );
}

export default SearchInput;
