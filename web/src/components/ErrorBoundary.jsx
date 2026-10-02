import { Component } from "react";
import * as Sentry from "@sentry/react";

class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    if (import.meta.env.VITE_SENTRY_DSN) {
      Sentry.captureException(error, {
        extra: { componentStack: errorInfo.componentStack },
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="font-body flex min-h-screen flex-col items-center justify-center gap-4 bg-bg px-6 text-center text-ink">
          <h1 className="font-heading m-0 text-heading-md font-semibold tracking-tight">
            Something went wrong
          </h1>
          <p className="m-0 max-w-md text-sm text-muted-600">
            An unexpected error stopped this page from loading. Reload the page
            to try again.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
          >
            Reload
          </button>
        </main>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
