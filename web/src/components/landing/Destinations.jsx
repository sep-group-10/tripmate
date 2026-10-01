import { unsplash } from "./unsplash";

const PLACES = [
  {
    name: "Sigiriya",
    region: "Central",
    note: "Climb the Lion Rock at sunrise",
    img: unsplash("photo-1711797750174-c3750dd9d7c9", 1400),
    span: "md:col-span-2 md:row-span-2",
  },
  {
    name: "Ella",
    region: "Uva",
    note: "Hill trains and tea country",
    img: unsplash("photo-1578519050142-afb511e518de"),
    span: "",
  },
  {
    name: "Yala",
    region: "South",
    note: "Leopards on safari",
    img: unsplash("photo-1728455470905-156f4278056a"),
    span: "",
  },
  {
    name: "Galle",
    region: "South",
    note: "Fort walls and stilt fishermen",
    img: unsplash("photo-1519566335946-e6f65f0f4fdf", 1400),
    span: "md:col-span-2",
  },
  {
    name: "Minneriya",
    region: "North Central",
    note: "The elephant gathering",
    img: unsplash("photo-1533484482814-3fe2d922be89"),
    span: "",
  },
  {
    name: "Jaffna",
    region: "North",
    note: "Lagoons and island ferries",
    img: unsplash("photo-1707236606614-fbee3070f156"),
    span: "",
  },
];

function Destinations() {
  return (
    <section className="mx-auto flex w-full max-w-[1120px] flex-col gap-9">
      <div className="grid grid-cols-1 items-end gap-5 md:grid-cols-2 md:gap-12">
        <div className="flex flex-col gap-2.5">
          <span className="text-eyebrow text-muted-600 uppercase">
            Who it&apos;s for
          </span>
          <h2 className="m-0 text-[clamp(28px,3.4vw,44px)] leading-[1.05] font-semibold tracking-[-0.03em] text-balance">
            Made for tourists exploring Sri Lanka
          </h2>
        </div>
        <div className="flex flex-col gap-2">
          <p className="m-0 text-[16.5px] leading-[1.6] text-muted-700 text-pretty">
            Whether you visit Sigiriya, Ella, Galle, or Jaffna, TripMate helps
            you plan a trip that fits your time and budget.
          </p>
          <p className="m-0 text-sm text-muted-600">
            Tourism information is managed by admins, so the data stays updated.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 auto-rows-[220px] grid-flow-dense gap-3 md:grid-cols-4">
        {PLACES.map((p) => (
          <div
            key={p.name}
            className={`group relative block overflow-hidden rounded-card bg-muted-900 shadow-control transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-card ${p.span}`}
          >
            <img
              src={p.img}
              alt={p.name}
              className="absolute inset-0 h-full w-full object-cover"
              loading="lazy"
            />
            <div className="absolute right-3 bottom-3 left-3 flex items-center justify-between gap-2.5 rounded-pill bg-surface py-2 pr-2 pl-4 shadow-raised">
              <div className="min-w-0">
                <div className="font-heading text-sm font-semibold tracking-tight text-ink">
                  {p.name}
                </div>
                <div className="overflow-hidden text-xs text-ellipsis whitespace-nowrap text-muted-600">
                  {p.note}
                </div>
              </div>
              <span className="flex-none rounded-badge bg-inset px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-muted-700 uppercase">
                {p.region}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Destinations;
