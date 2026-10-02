function EmptyState({ title, message, children }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-1.5 rounded-xl bg-inset px-6 py-16 text-center">
      <span className="font-heading text-md font-semibold">{title}</span>
      <span className="text-body-sm text-muted-600">{message}</span>
      {children && <div className="mt-3">{children}</div>}
    </div>
  );
}

export default EmptyState;
