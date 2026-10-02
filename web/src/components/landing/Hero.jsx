import { useState } from "react";
import { Link } from "react-router-dom";
import { unsplash } from "./unsplash";

const HERO_STOPS = [
  { name: "Nine Arches Bridge", time: "07:30", dur: "1 hr", cost: "Free" },
  { name: "Little Adam's Peak", time: "09:15", dur: "2 hr", cost: "Free" },
  {
    name: "Lunch in Ella town",
    time: "12:30",
    dur: "1 hr",
    cost: "LKR 2,400",
  },
];

function Hero() {
  const [prompt, setPrompt] = useState("");

  return (
    <section id="top" className="px-3 pt-3">
      <div className="relative min-h-[620px] overflow-hidden rounded-card bg-muted-900 md:min-h-[72vh]">
        <img
          src={unsplash("photo-1566296314736-6eaac1ca0cb9", 2000)}
          alt="Blue train crossing the Nine Arches Bridge in Ella"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-[rgba(23,25,26,0.38)]" />
        <div className="relative mx-auto grid w-full max-w-[1120px] grid-cols-1 items-end gap-9 px-5 pt-[120px] pb-8 md:grid-cols-2 md:pb-14">
          <div className="flex flex-col gap-5 text-white">
            <span className="flex items-center gap-2 font-mono text-eyebrow tracking-widest uppercase">
              <span className="h-0.5 w-5.5 bg-[#c08a2e]" />
              Nine Arches Bridge, Ella
            </span>
            <h1 className="m-0 text-[clamp(40px,6vw,72px)] leading-[1] font-semibold tracking-[-0.035em] text-balance">
              Plan your Sri Lanka trip in minutes, not hours.
            </h1>
            <p className="m-0 max-w-[500px] text-lg leading-[1.55] text-white/92 text-pretty">
              Tell TripMate where you want to go, when, and your budget. Our AI
              builds a day-by-day plan for you.
            </p>
            <div className="flex max-w-[520px] items-center gap-1.5 rounded-pill bg-surface py-1.5 pr-1.5 pl-4.5 shadow-card">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--color-muted-500)"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
                className="flex-none"
              >
                <path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z" />
              </svg>
              <input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="4 days in the hills, love tea and hiking"
                className="min-w-0 flex-1 border-0 bg-transparent px-1 py-2.5 font-body text-sm text-ink outline-none"
              />
              <Link
                to="/register"
                className="flex-none rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white no-underline hover:bg-accent-600"
              >
                Plan my trip
              </Link>
            </div>
            <span className="text-sm text-white/85">
              Free to use. Just plan — nothing to buy.
            </span>
          </div>

          <div className="hidden w-full max-w-[360px] flex-col gap-3.5 justify-self-end rounded-card bg-surface p-4.5 shadow-card md:flex">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-mono text-eyebrow text-muted-600 uppercase">
                  Day 2 · Ella
                </span>
                <div className="mt-0.5 font-heading text-lg font-semibold tracking-tight">
                  Bridges &amp; tea hills
                </div>
              </div>
              <span className="rounded-badge bg-success-100 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-success-700 uppercase">
                Sunny 26°
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              {HERO_STOPS.map((s, i) => (
                <div
                  key={s.name}
                  className={`flex items-center gap-3 rounded-panel p-2 ${i === 0 ? "bg-inset" : ""}`}
                >
                  <div className="h-11 w-11 flex-none rounded-[10px] bg-muted-200" />
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium">{s.name}</div>
                    <div className="num text-xs text-muted-600">
                      {s.time} · {s.dur}
                    </div>
                  </div>
                  <span className="num text-[12.5px] text-muted-700">
                    {s.cost}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between border-t border-divider pt-3">
              <span className="text-sm text-muted-600">Estimated day cost</span>
              <span className="num font-heading text-[17px] font-semibold">
                LKR 9,800
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
