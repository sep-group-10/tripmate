import { Construction } from "lucide-react";

function ComingSoon({ title }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-card bg-surface py-24 text-center shadow-card">
      <span className="flex h-12 w-12 items-center justify-center rounded-pill bg-muted-300 text-muted-700">
        <Construction size={22} />
      </span>
      <h1 className="font-heading text-heading-sm font-semibold text-ink">
        {title}
      </h1>
      <p className="max-w-sm text-body-sm text-muted-600">
        This section is coming soon.
      </p>
    </div>
  );
}

export default ComingSoon;
