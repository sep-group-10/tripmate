import { useState } from "react";
import { Sun, Cloud, CloudDrizzle } from "lucide-react";

const FORECAST = [
  { d: "MON", t: "29°", Icon: Sun, color: "text-warn" },
  { d: "TUE", t: "28°", Icon: Cloud, color: "text-muted-600" },
  { d: "WED", t: "24°", Icon: CloudDrizzle, color: "text-info" },
  { d: "THU", t: "30°", Icon: Sun, color: "text-warn" },
];

const ROUTE = [
  { n: 1, place: "Kandy", km: "Start" },
  { n: 2, place: "Nuwara Eliya", km: "77 km" },
  { n: 3, place: "Ella", km: "58 km" },
];

const INTEREST_OPTIONS = [
  "Tea",
  "Hiking",
  "Beaches",
  "Temples",
  "Wildlife",
  "Food",
];

const SAVED = [
  { name: "Hill country loop", meta: "4 days · Mar 12" },
  { name: "South coast slow week", meta: "7 days · Draft" },
];

function Features() {
  const [tags, setTags] = useState({ Tea: true, Hiking: true });

  return (
    <section
      id="features"
      className="mx-auto flex w-full max-w-[1120px] scroll-mt-24 flex-col gap-9"
    >
      <div className="flex flex-col gap-2.5">
        <span className="text-eyebrow text-muted-600 uppercase">Features</span>
        <h2 className="m-0 max-w-[640px] text-[clamp(28px,3.4vw,44px)] leading-[1.05] font-semibold tracking-[-0.03em] text-balance">
          Everything you need to plan your trip
        </h2>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div className="flex min-h-[260px] flex-col justify-between gap-7 rounded-card bg-muted-900 p-7 text-white md:col-span-2">
          <div className="flex max-w-[360px] flex-col gap-2">
            <span className="h-0.5 w-7 bg-[#c08a2e]" />
            <h3 className="mt-1.5 mb-0 font-heading text-xl font-semibold tracking-tight">
              Budget aware
            </h3>
            <p className="m-0 text-[15px] leading-[1.55] text-muted-300">
              See the estimated cost and stay within your budget.
            </p>
          </div>
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <span className="num font-heading text-[clamp(30px,4vw,44px)] font-semibold tracking-[-0.03em]">
                LKR 74,200{" "}
                <span className="text-sm font-normal tracking-normal text-muted-400">
                  estimated
                </span>
              </span>
              <span className="num text-sm text-[#c08a2e]">of LKR 80,000</span>
            </div>
            <div className="h-2 overflow-hidden rounded-pill bg-white/12">
              <div className="h-full w-[93%] rounded-pill bg-accent" />
            </div>
            <div className="flex flex-wrap gap-4.5 text-[12.5px] text-muted-300">
              <span className="num">Stays 41,000</span>
              <span className="num">Food 18,600</span>
              <span className="num">Travel 14,600</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-4.5 rounded-card bg-surface p-6 shadow-control">
          <div className="flex flex-col gap-1.5">
            <h3 className="m-0 font-heading text-lg font-semibold tracking-tight">
              Weather check
            </h3>
            <p className="m-0 text-[14.5px] leading-[1.55] text-muted-700">
              Your plan is checked against the weather for your dates.
            </p>
          </div>
          <div className="mt-auto grid grid-cols-4 gap-1.5">
            {FORECAST.map((f) => (
              <div
                key={f.d}
                className="flex flex-col items-center gap-1.5 rounded-xl bg-inset px-1 py-2.5"
              >
                <span className="font-mono text-[10.5px] text-muted-600">
                  {f.d}
                </span>
                <f.Icon size={20} aria-hidden="true" className={f.color} />
                <span className="num text-[13px] font-medium">{f.t}</span>
              </div>
            ))}
          </div>
          <span className="self-start rounded-badge bg-warn-100 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-warn-700 uppercase">
            Rain Wed · moved indoors
          </span>
        </div>

        <div className="flex flex-col gap-4.5 rounded-card bg-surface p-6 shadow-control">
          <div className="flex flex-col gap-1.5">
            <h3 className="m-0 font-heading text-lg font-semibold tracking-tight">
              Smart routes
            </h3>
            <p className="m-0 text-[14.5px] leading-[1.55] text-muted-700">
              Places are ordered to save travel time.
            </p>
          </div>
          <div className="mt-auto flex flex-col">
            {ROUTE.map((r, i) => (
              <div key={r.n} className="flex gap-3">
                <div className="flex w-5.5 flex-col items-center">
                  <span className="num flex h-5.5 w-5.5 items-center justify-center rounded-pill bg-info text-[11px] font-semibold text-white">
                    {r.n}
                  </span>
                  <span
                    className={`min-h-3.5 w-0.5 flex-1 ${i < ROUTE.length - 1 ? "bg-info-300" : "bg-transparent"}`}
                  />
                </div>
                <div className="flex flex-1 justify-between gap-2.5 pb-3">
                  <span className="text-sm font-medium">{r.place}</span>
                  <span className="num text-[12.5px] text-muted-600">
                    {r.km}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-4.5 rounded-card bg-surface p-6 shadow-control">
          <div className="flex flex-col gap-1.5">
            <h3 className="m-0 font-heading text-lg font-semibold tracking-tight">
              Personal plans
            </h3>
            <p className="m-0 text-[14.5px] leading-[1.55] text-muted-700">
              Plans that match your likes and travel style.
            </p>
          </div>
          <div className="mt-auto flex flex-wrap gap-1.5">
            {INTEREST_OPTIONS.map((label) => {
              const on = !!tags[label];
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => setTags((t) => ({ ...t, [label]: !on }))}
                  className={`rounded-full px-3.5 py-2 text-[13px] font-medium ${
                    on ? "bg-muted-900 text-white" : "bg-inset text-muted-800"
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col gap-4.5 rounded-card bg-surface p-6 shadow-control">
          <div className="flex flex-col gap-1.5">
            <h3 className="m-0 font-heading text-lg font-semibold tracking-tight">
              AI assistant
            </h3>
            <p className="m-0 text-[14.5px] leading-[1.55] text-muted-700">
              Ask questions and change your plan by chatting.
            </p>
          </div>
          <div className="mt-auto flex flex-col gap-2">
            <div className="self-end rounded-[14px_14px_4px_14px] border border-muted-200 bg-inset px-3 py-2 text-[13px]">
              Is Sigiriya too hot at noon?
            </div>
            <div className="max-w-[90%] self-start rounded-[14px_14px_14px_4px] border border-divider bg-surface px-3 py-2 text-[13px]">
              Yes — I moved the climb to 7:00.
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-4.5 rounded-card bg-surface p-6 shadow-control">
          <div className="flex flex-col gap-1.5">
            <h3 className="m-0 font-heading text-lg font-semibold tracking-tight">
              Save your trips
            </h3>
            <p className="m-0 text-[14.5px] leading-[1.55] text-muted-700">
              Keep your trips and edit them later.
            </p>
          </div>
          <div className="mt-auto flex flex-col gap-1.5">
            {SAVED.map((s) => (
              <div
                key={s.name}
                className="flex items-center gap-2.5 rounded-xl bg-inset p-1.5"
              >
                <div className="h-9.5 w-9.5 flex-none rounded-[9px] bg-muted-200" />
                <div className="min-w-0 flex-1">
                  <div className="text-[13.5px] font-medium">{s.name}</div>
                  <div className="num text-[11.5px] text-muted-600">
                    {s.meta}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <p className="-mt-4 mb-0 text-sm text-muted-600">
        Costs are estimates. Prices may change.
      </p>
    </section>
  );
}

export default Features;
