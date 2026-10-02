import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";

const PLAN_DAYS = [
  { day: "DAY 1", place: "Kandy · Temple of the Tooth", cost: "LKR 16k" },
  { day: "DAY 2", place: "Nuwara Eliya · Tea estate", cost: "LKR 21k" },
  { day: "DAY 3", place: "Ella · Nine Arches", cost: "LKR 18k" },
];

function HowItWorks() {
  return (
    <section
      id="how"
      className="mx-auto flex w-full max-w-[1120px] scroll-mt-24 flex-col gap-9"
    >
      <div className="flex flex-wrap items-end justify-between gap-5">
        <div className="flex flex-col gap-2.5">
          <span className="text-eyebrow text-muted-600 uppercase">
            How it works
          </span>
          <h2 className="m-0 text-[clamp(28px,3.4vw,44px)] leading-[1.05] font-semibold tracking-[-0.03em]">
            Your trip in 3 easy steps
          </h2>
        </div>
        <Link
          to="/register"
          className="rounded-full bg-muted-900 px-5 py-2.5 text-sm font-medium text-white no-underline"
        >
          Try it now
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <article className="flex flex-col gap-5 rounded-card bg-surface p-2.5 shadow-control">
          <div className="flex h-[200px] flex-col justify-end gap-2.5 rounded-panel bg-inset p-4.5">
            <div className="max-w-[85%] self-end rounded-[14px_14px_4px_14px] border border-divider bg-surface px-3.5 py-2.5 text-[13.5px] leading-[1.45]">
              4 days in March, two of us, love tea &amp; hikes. Around LKR
              80,000.
            </div>
            <div className="flex items-center gap-2 self-start">
              <span className="flex h-6 w-6 items-center justify-center rounded-[7px] bg-accent text-white">
                <MapPin size={12} aria-hidden="true" />
              </span>
              <span className="flex gap-1 rounded-pill bg-surface px-3 py-2.5">
                <span className="h-1.5 w-1.5 animate-pulse rounded-pill bg-muted-500" />
                <span className="h-1.5 w-1.5 animate-pulse rounded-pill bg-muted-500 [animation-delay:0.2s]" />
                <span className="h-1.5 w-1.5 animate-pulse rounded-pill bg-muted-500 [animation-delay:0.4s]" />
              </span>
            </div>
          </div>
          <div className="flex flex-col gap-2 px-3 pb-3.5">
            <span className="num font-mono text-xs tracking-wider text-accent-700">
              STEP 01
            </span>
            <h3 className="m-0 font-heading text-xl font-semibold tracking-tight">
              Tell us your trip
            </h3>
            <p className="m-0 text-[15px] leading-[1.55] text-muted-700">
              Chat with the AI. Share your dates, budget, and what you like.
            </p>
          </div>
        </article>

        <article className="flex flex-col gap-5 rounded-card bg-surface p-2.5 shadow-control">
          <div className="flex h-[200px] flex-col justify-center gap-1.5 rounded-panel bg-inset p-3.5">
            {PLAN_DAYS.map((d) => (
              <div
                key={d.day}
                className="flex items-center gap-2.5 rounded-[10px] bg-surface px-2.5 py-2 shadow-control"
              >
                <span className="num w-9.5 font-mono text-[11px] text-muted-500">
                  {d.day}
                </span>
                <span className="flex-1 text-[13.5px] font-medium">
                  {d.place}
                </span>
                <span className="num text-xs text-muted-600">{d.cost}</span>
              </div>
            ))}
          </div>
          <div className="flex flex-col gap-2 px-3 pb-3.5">
            <span className="num font-mono text-xs tracking-wider text-accent-700">
              STEP 02
            </span>
            <h3 className="m-0 font-heading text-xl font-semibold tracking-tight">
              Get your plan
            </h3>
            <p className="m-0 text-[15px] leading-[1.55] text-muted-700">
              The AI builds a day-by-day plan with places, routes, and cost.
            </p>
          </div>
        </article>

        <article className="flex flex-col gap-5 rounded-card bg-surface p-2.5 shadow-control">
          <div className="flex h-[200px] flex-col justify-center gap-3 rounded-panel bg-inset p-4.5">
            <div className="max-w-[85%] self-end rounded-[14px_14px_4px_14px] border border-divider bg-surface px-3.5 py-2.5 text-[13.5px]">
              Swap day 3 for a beach day?
            </div>
            <div className="flex items-center gap-2.5 rounded-[10px] bg-surface px-2.5 py-2 shadow-control">
              <span className="num w-9.5 font-mono text-[11px] text-muted-500">
                DAY 3
              </span>
              <span className="flex-1 text-[13.5px] font-medium">
                <span className="font-normal text-muted-500 line-through">
                  Ella
                </span>{" "}
                → Mirissa
              </span>
              <span className="rounded-badge bg-success-100 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-success-700 uppercase">
                Updated
              </span>
            </div>
          </div>
          <div className="flex flex-col gap-2 px-3 pb-3.5">
            <span className="num font-mono text-xs tracking-wider text-accent-700">
              STEP 03
            </span>
            <h3 className="m-0 font-heading text-xl font-semibold tracking-tight">
              Change it anytime
            </h3>
            <p className="m-0 text-[15px] leading-[1.55] text-muted-700">
              Not happy? Ask the AI to change a day, a place, or the budget.
            </p>
          </div>
        </article>
      </div>
    </section>
  );
}

export default HowItWorks;
