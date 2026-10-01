/** Row list for an activity/audit-style feed: a tag badge, a title +
 * meta line, and a trailing relative timestamp. */
function ActivityList({ items }) {
  return (
    <div className="flex flex-col">
      {items.map((item) => (
        <div
          key={item.title}
          className="flex items-center gap-3.5 border-b border-divider px-7 py-3.5 last:border-b-0"
        >
          <span className="min-w-18.5 justify-center rounded-badge bg-muted-300 px-2 py-1 text-center font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
            {item.kind}
          </span>
          <div className="min-w-0 flex-1">
            <div className="text-body-sm font-medium text-ink">
              {item.title}
            </div>
            <div className="text-helper text-muted-600">{item.meta}</div>
          </div>
          <span className="whitespace-nowrap text-helper text-muted-500">
            {item.time}
          </span>
        </div>
      ))}
    </div>
  );
}

export default ActivityList;
