/** TripMate brand mark: app icon plus the two-tone wordmark. */
function Logo({ textClassName = "text-lg" }) {
  return (
    <span className="flex items-center gap-2.5">
      <img
        src="/logo-icon.png"
        alt=""
        width={32}
        height={32}
        className="h-logo w-logo rounded-lg"
      />
      <span
        className={`font-heading font-bold tracking-tight text-ink ${textClassName}`}
      >
        Trip<span className="text-accent">Mate</span>
      </span>
    </span>
  );
}

export default Logo;
