import { Monitor, Smartphone } from "lucide-react";
import { unsplash } from "./unsplash";

function Platforms() {
  return (
    <section className="mx-auto w-full max-w-[1120px]">
      <div className="grid grid-cols-1 items-center gap-10 overflow-hidden rounded-card bg-surface p-6 shadow-raised md:grid-cols-2 md:p-12">
        <div className="flex flex-col gap-5.5">
          <h2 className="m-0 text-[clamp(28px,3.4vw,40px)] leading-[1.05] font-semibold tracking-[-0.03em]">
            Use it on web and mobile
          </h2>
          <div className="flex flex-col gap-2.5">
            <div className="flex items-center gap-3.5 rounded-panel bg-inset px-4.5 py-4">
              <Monitor size={22} aria-hidden="true" />
              <span className="flex-1 font-medium">Web app</span>
              <span className="rounded-badge bg-success-100 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-success-700 uppercase">
                Available
              </span>
            </div>
            <div className="flex items-center gap-3.5 rounded-panel bg-inset px-4.5 py-4">
              <Smartphone size={22} aria-hidden="true" />
              <span className="flex-1 font-medium">Mobile app</span>
              <span className="rounded-badge bg-warn-100 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-warn-700 uppercase">
                Coming soon
              </span>
            </div>
          </div>
        </div>
        <div className="relative flex h-[440px] items-start justify-center">
          <img
            src={unsplash("photo-1580910527739-556eb89f9d65", 1200)}
            alt="Palm-lined beach"
            loading="lazy"
            className="absolute inset-0 h-full w-full rounded-card object-cover"
          />
          <div className="relative mt-7 h-[520px] w-[254px] rounded-[40px] bg-muted-900 p-2 shadow-card">
            <div className="h-full w-full overflow-hidden rounded-[32px] bg-bg" />
          </div>
        </div>
      </div>
    </section>
  );
}

export default Platforms;
