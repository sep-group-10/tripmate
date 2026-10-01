import { Link } from "react-router-dom";
import { unsplash } from "./unsplash";

function FinalCta() {
  return (
    <section className="mx-auto w-full max-w-[1120px]">
      <div className="relative grid grid-cols-1 overflow-hidden rounded-card bg-muted-900 text-white md:grid-cols-2">
        <div className="flex flex-col justify-center gap-4.5 p-9 md:p-16">
          <span className="h-0.5 w-10 bg-[#c08a2e]" />
          <h2 className="m-0 text-[clamp(32px,4.4vw,52px)] leading-[1.02] font-semibold tracking-[-0.035em] text-balance">
            Ready to plan your Sri Lanka trip?
          </h2>
          <p className="m-0 max-w-[420px] text-lg leading-[1.55] text-muted-300">
            Create your free account and let TripMate do the planning.
          </p>
          <Link
            to="/register"
            className="mt-2 self-start rounded-full bg-accent px-6 py-3.5 text-md font-medium text-white no-underline hover:bg-accent-600"
          >
            Plan my trip
          </Link>
        </div>
        <div className="relative min-h-[340px]">
          <img
            src={unsplash("photo-1612862862126-865765df2ded", 1400)}
            alt="Sigiriya rock fortress from above"
            loading="lazy"
            className="absolute inset-0 h-full w-full object-cover"
          />
        </div>
      </div>
    </section>
  );
}

export default FinalCta;
