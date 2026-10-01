import { ShoppingBag, Wallet, CloudRain } from "lucide-react";
import { unsplash } from "./unsplash";

const PROBLEMS = [
  {
    Icon: ShoppingBag,
    text: "You open many websites to find places, hotels, and food.",
  },
  {
    Icon: Wallet,
    text: "It is hard to keep the plan inside your budget.",
  },
  {
    Icon: CloudRain,
    text: "You do not know if the weather or the travel time will spoil the plan.",
  },
];

function Problem() {
  return (
    <section className="mx-auto grid w-full max-w-[1120px] grid-cols-1 items-stretch gap-5 md:grid-cols-2">
      <div className="flex flex-col gap-7 rounded-card bg-inset p-6 md:p-10">
        <div className="flex flex-col gap-2.5">
          <span className="text-eyebrow text-muted-600 uppercase">
            The usual way
          </span>
          <h2 className="m-0 text-[clamp(28px,3.4vw,40px)] leading-[1.08] font-semibold tracking-[-0.03em]">
            Planning a trip is tiring
          </h2>
        </div>
        <div className="flex flex-col gap-4.5">
          {PROBLEMS.map(({ Icon, text }) => (
            <div key={text} className="flex items-start gap-3.5">
              <span className="flex h-9.5 w-9.5 flex-none items-center justify-center rounded-xl bg-surface text-muted-700 shadow-control">
                <Icon size={19} aria-hidden="true" />
              </span>
              <p className="mt-2 mb-0 text-base leading-[1.5] text-muted-800 text-pretty">
                {text}
              </p>
            </div>
          ))}
        </div>
      </div>
      <div className="relative flex min-h-[380px] items-end overflow-hidden rounded-card bg-muted-900 p-5 md:p-8">
        <img
          src={unsplash("photo-1609681980718-340e7f4b11d7", 1400)}
          alt="Waterfall in the Sri Lankan hills"
          loading="lazy"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="relative flex max-w-[380px] flex-col gap-3 rounded-card bg-surface p-5 shadow-card">
          <span className="text-eyebrow text-accent-700 uppercase">
            With TripMate
          </span>
          <p className="m-0 font-heading text-xl leading-[1.2] font-semibold tracking-[-0.02em]">
            TripMate does this work for you.
          </p>
          <div className="flex flex-wrap gap-1.5">
            <span className="rounded-pill bg-success-100 px-2.5 py-1 text-xs font-medium text-success-700">
              One place
            </span>
            <span className="rounded-pill bg-info-100 px-2.5 py-1 text-xs font-medium text-info-700">
              Inside budget
            </span>
            <span className="rounded-pill bg-warn-100 px-2.5 py-1 text-xs font-medium text-warn-700">
              Weather checked
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Problem;
