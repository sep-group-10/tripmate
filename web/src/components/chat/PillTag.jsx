import { PILL_TONES } from "../../utils/pillTones";

function PillTag({ tone, children, className = "" }) {
  return (
    <span
      className={`flex-none rounded-pill px-2.5 py-1 text-caption font-medium ${PILL_TONES[tone] || PILL_TONES.outline} ${className}`}
    >
      {children}
    </span>
  );
}

export default PillTag;
