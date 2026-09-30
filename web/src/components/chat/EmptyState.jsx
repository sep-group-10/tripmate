function EmptyState({ what }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-1.5 rounded-xl bg-inset px-6 py-16 text-center">
      <span className="font-heading text-md font-semibold">No {what} yet</span>
      <span className="text-body-sm text-muted-600">
        Plan a trip in the chat to see your {what} here.
      </span>
    </div>
  );
}

export default EmptyState;
