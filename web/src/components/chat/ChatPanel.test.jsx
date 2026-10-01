import { describe, it, expect, vi, beforeEach } from "vitest";
import { act, fireEvent, render, screen } from "@testing-library/react";
import ChatPanel from "./ChatPanel";
import { sendChatMessage } from "../../services/chatService";

vi.mock("../../services/chatService", () => ({ sendChatMessage: vi.fn() }));

const clearSession = vi.fn();
vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ clearSession }),
}));

const FAILURE_TEXT = "Sorry, I couldn't reach the planner. Please try again.";

// A promise the test settles by hand, to hold a request "in flight".
function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

const reply = (text, extra = {}) => ({
  assistant_message: text,
  session: {
    id: "session-1",
    status: "pending",
    iteration_count: 0,
    progress_message: null,
    progress_percentage: 0,
  },
  itinerary: null,
  ...extra,
});

const apiError = (status, code) => {
  const error = new Error(`status ${status}`);
  error.response = {
    status,
    data: { success: false, error: { code, message: "ignored" } },
  };
  return error;
};

const input = () => screen.getByLabelText("Message");
const sendButton = () => screen.getByRole("button", { name: "Send message" });
const type = (text) => fireEvent.change(input(), { target: { value: text } });
const pressEnter = (options = {}) =>
  fireEvent.keyDown(input(), { key: "Enter", ...options });

// Types a message, presses Enter, and lets the request promise settle.
async function send(text) {
  type(text);
  await act(async () => {
    pressEnter();
  });
}

beforeEach(() => {
  vi.mocked(sendChatMessage).mockReset();
  clearSession.mockClear();
});

describe("ChatPanel", () => {
  it("shows the welcome message first", () => {
    render(<ChatPanel onPlan={vi.fn()} />);
    expect(screen.getByText(/Tell me where you'd like to go/)).toBeVisible();
  });

  it("shows a sent message and clears the input", async () => {
    sendChatMessage.mockResolvedValue(reply("Got it"));
    render(<ChatPanel onPlan={vi.fn()} />);
    await send("Plan a 5-day trip to Kandy and Ella");
    expect(
      screen.getByText("Plan a 5-day trip to Kandy and Ella"),
    ).toBeVisible();
    expect(input()).toHaveValue("");
  });

  it("disables Send when the input is empty or only spaces", () => {
    render(<ChatPanel onPlan={vi.fn()} />);
    expect(sendButton()).toBeDisabled();
    type("   ");
    expect(sendButton()).toBeDisabled();
    type("hello");
    expect(sendButton()).toBeEnabled();
  });

  it("disables Send, the input and the chips while waiting for a reply", async () => {
    const pending = deferred();
    sendChatMessage.mockReturnValue(pending.promise);
    render(<ChatPanel onPlan={vi.fn()} />);
    await send("hello");

    expect(input()).toBeDisabled();
    expect(sendButton()).toBeDisabled();
    expect(screen.getByRole("button", { name: "Swap a day" })).toBeDisabled();

    await act(async () => pending.resolve(reply("Hi")));
    expect(input()).toBeEnabled();
    expect(screen.getByRole("button", { name: "Swap a day" })).toBeEnabled();
  });

  it("sends on Enter", async () => {
    sendChatMessage.mockResolvedValue(reply("ok"));
    render(<ChatPanel onPlan={vi.fn()} />);
    await send("hello");
    expect(sendChatMessage).toHaveBeenCalledTimes(1);
    expect(sendChatMessage).toHaveBeenCalledWith("hello", null);
  });

  it("does not send on Shift+Enter", () => {
    render(<ChatPanel onPlan={vi.fn()} />);
    type("line one");
    pressEnter({ shiftKey: true });
    expect(sendChatMessage).not.toHaveBeenCalled();
    expect(input()).toHaveValue("line one");
  });

  it("sends once even if Enter is pressed twice quickly", async () => {
    const pending = deferred();
    sendChatMessage.mockReturnValue(pending.promise);
    render(<ChatPanel onPlan={vi.fn()} />);
    type("hello");
    await act(async () => {
      pressEnter();
      pressEnter();
    });
    expect(sendChatMessage).toHaveBeenCalledTimes(1);
    await act(async () => pending.resolve(reply("ok")));
  });

  it("shows the thinking indicator while waiting and hides it after", async () => {
    const pending = deferred();
    sendChatMessage.mockReturnValue(pending.promise);
    render(<ChatPanel onPlan={vi.fn()} />);
    await send("hello");
    expect(screen.getByText("TripMate is thinking…")).toBeVisible();

    await act(async () => pending.resolve(reply("Hi there")));
    expect(screen.queryByText("TripMate is thinking…")).not.toBeInTheDocument();
  });

  it("shows TripMate's reply", async () => {
    sendChatMessage.mockResolvedValue(reply("Here is your plan"));
    render(<ChatPanel onPlan={vi.fn()} />);
    await send("hello");
    expect(screen.getByText("Here is your plan")).toBeVisible();
  });

  it("hands a returned itinerary to onPlan, and keeps it on a null reply", async () => {
    const onPlan = vi.fn();
    const itinerary = { status: "completed", days: [] };
    sendChatMessage.mockResolvedValueOnce(reply("Plan", { itinerary }));
    sendChatMessage.mockResolvedValueOnce(reply("Question"));
    render(<ChatPanel onPlan={onPlan} />);
    await send("first");
    await send("second");
    expect(onPlan).toHaveBeenCalledTimes(1);
    expect(onPlan).toHaveBeenCalledWith(itinerary);
  });

  it("continues the same session after the first reply", async () => {
    sendChatMessage.mockResolvedValue(reply("ok"));
    render(<ChatPanel onPlan={vi.fn()} />);
    await send("first");
    await send("second");
    expect(sendChatMessage).toHaveBeenNthCalledWith(1, "first", null);
    expect(sendChatMessage).toHaveBeenNthCalledWith(2, "second", "session-1");
  });

  describe("when the request fails", () => {
    it("keeps the user's message, shows the error with Retry, and re-enables the input", async () => {
      sendChatMessage.mockRejectedValue(new Error("Network Error"));
      render(<ChatPanel onPlan={vi.fn()} />);
      await send("Plan my trip");

      expect(screen.getByText("Plan my trip")).toBeVisible();
      expect(screen.getByText(FAILURE_TEXT)).toBeVisible();
      expect(screen.getByRole("button", { name: "Retry" })).toBeVisible();
      expect(
        screen.queryByText("TripMate is thinking…"),
      ).not.toBeInTheDocument();
      expect(input()).toBeEnabled();
      type("another");
      expect(sendButton()).toBeEnabled();
    });

    it("Retry resends the same message without duplicating it", async () => {
      sendChatMessage.mockRejectedValueOnce(new Error("Network Error"));
      sendChatMessage.mockResolvedValueOnce(reply("Here you go"));
      render(<ChatPanel onPlan={vi.fn()} />);
      await send("Plan my trip");

      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Retry" }));
      });

      expect(sendChatMessage).toHaveBeenCalledTimes(2);
      expect(sendChatMessage).toHaveBeenNthCalledWith(1, "Plan my trip", null);
      expect(sendChatMessage).toHaveBeenNthCalledWith(2, "Plan my trip", null);
      expect(screen.getAllByText("Plan my trip")).toHaveLength(1);
      expect(screen.queryByText(FAILURE_TEXT)).not.toBeInTheDocument();
      expect(screen.getByText("Here you go")).toBeVisible();
    });

    it("sends the user to login when the session is gone (401)", async () => {
      sendChatMessage.mockRejectedValue(apiError(401, "TOKEN_EXPIRED"));
      render(<ChatPanel onPlan={vi.fn()} />);
      await send("hello");
      expect(clearSession).toHaveBeenCalledTimes(1);
      expect(screen.queryByText(FAILURE_TEXT)).not.toBeInTheDocument();
    });

    it("starts a new session after NOT_FOUND", async () => {
      sendChatMessage.mockResolvedValueOnce(reply("first reply"));
      sendChatMessage.mockRejectedValueOnce(apiError(404, "NOT_FOUND"));
      sendChatMessage.mockResolvedValueOnce(reply("fresh"));
      render(<ChatPanel onPlan={vi.fn()} />);
      await send("one");
      await send("two");
      expect(screen.getByText(/planning session has expired/)).toBeVisible();
      await send("three");
      expect(sendChatMessage).toHaveBeenNthCalledWith(2, "two", "session-1");
      expect(sendChatMessage).toHaveBeenNthCalledWith(3, "three", null);
    });

    it("does not offer Retry for a message the server rejected", async () => {
      sendChatMessage.mockRejectedValue(apiError(400, "VALIDATION_ERROR"));
      render(<ChatPanel onPlan={vi.fn()} />);
      await send("hello");
      expect(screen.getByText(/couldn't process that message/)).toBeVisible();
      expect(
        screen.queryByRole("button", { name: "Retry" }),
      ).not.toBeInTheDocument();
    });
  });

  describe("suggestion chips", () => {
    it("sends the chip's text as a message", async () => {
      sendChatMessage.mockResolvedValue(reply("Swapped"));
      render(<ChatPanel onPlan={vi.fn()} />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Swap a day" }));
      });
      expect(sendChatMessage).toHaveBeenCalledWith("Swap a day", null);
      expect(screen.getByText("Swap a day", { selector: "p" })).toBeVisible();
      expect(input()).toHaveValue("");
    });
  });
});
