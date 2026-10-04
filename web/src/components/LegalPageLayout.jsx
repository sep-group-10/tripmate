import { Link } from "react-router-dom";
import { ArrowLeft, MapPin } from "lucide-react";

/** Shared chrome for standalone legal/policy pages (Terms, Privacy) -
 * same header/back-link shell, just the prose body differs per page. */
function LegalPageLayout({ title, lastUpdated, children }) {
  return (
    <div className="font-body min-h-screen bg-bg px-6 py-12 text-ink">
      <div className="mx-auto flex w-full max-w-[720px] flex-col gap-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-logo w-logo items-center justify-center rounded-lg bg-accent text-white">
            <MapPin size={15} aria-hidden="true" />
          </span>
          <span className="font-heading text-lg font-semibold tracking-tight">
            TripMate
          </span>
        </div>

        <section className="flex flex-col gap-6 rounded-card bg-surface p-8 shadow-card">
          <div className="flex flex-col gap-1.5">
            <Link
              to="/"
              className="flex w-fit items-center gap-1.5 text-sm text-muted-600"
            >
              <ArrowLeft size={14} aria-hidden="true" />
              Back to home
            </Link>
            <h1 className="font-heading mt-2 mb-0 text-heading-md font-semibold tracking-tight">
              {title}
            </h1>
            <p className="m-0 text-sm text-muted-600">
              Last updated {lastUpdated}
            </p>
          </div>

          <div className="legal-prose flex flex-col gap-5 text-[15px] leading-relaxed text-muted-800">
            {children}
          </div>
        </section>
      </div>
    </div>
  );
}

export default LegalPageLayout;
