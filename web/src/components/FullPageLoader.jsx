function FullPageLoader() {
  return (
    <main
      className="font-body flex min-h-screen items-center justify-center bg-bg text-ink"
      role="status"
      aria-live="polite"
      aria-label="Loading your session"
    >
      <span className="h-10 w-10 animate-spin rounded-full border-4 border-muted-300 border-t-accent" />
      <span className="sr-only">Loading your session…</span>
    </main>
  );
}

export default FullPageLoader;
