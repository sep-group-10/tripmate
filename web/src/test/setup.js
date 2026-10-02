import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(() => {
  cleanup();
});

// jsdom doesn't implement scrolling; the chat calls scrollIntoView on new
// messages.
Element.prototype.scrollIntoView = vi.fn();
