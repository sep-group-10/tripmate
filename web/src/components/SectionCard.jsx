function SectionCard({ title, badge, children }) {
  return (
    <section className="overflow-hidden rounded-card bg-surface shadow-control">
      <div className="flex items-center justify-between gap-4 border-b border-divider px-7 py-4.5">
        <h2 className="font-heading m-0 text-[17px] font-semibold tracking-tight">
          {title}
        </h2>
        <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
          {badge}
        </span>
      </div>
      <div className="flex flex-col gap-6 p-7">{children}</div>
    </section>
  );
}

export default SectionCard;
