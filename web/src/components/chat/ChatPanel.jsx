import { useEffect, useRef, useState } from "react";
import { SendHorizontal } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { sendChatMessage } from "../../services/chatService";
import { describeChatError } from "../../utils/chatErrors";

const SUGGESTIONS = ["Swap a day", "Cut LKR 10,000", "Add a tea estate visit"];

const MAX_INPUT_HEIGHT_PX = 144;

const WELCOME_MESSAGES = [
  {
    id: "welcome",
    role: "assistant",
    text: "Hi! Tell me where you'd like to go, for how long and what you enjoy, and I'll plan it for you.",
  },
];

function ItineraryPreview({ day }) {
  return (
    <div className="mt-3 rounded-lg bg-bg p-3.5">
      <span className="text-eyebrow font-medium tracking-wide text-muted-600 uppercase">
        Day {day.day_number} · {day.date}
      </span>
      <ul className="m-0 mt-2 flex list-none flex-col gap-2 p-0">
        {day.items.map((item) => (
          <li key={item.candidate_id} className="flex items-baseline gap-3">
            <span className="w-25 flex-none font-mono text-caption text-muted-600">
              {item.start_time}–{item.end_time}
            </span>
            <span className="text-body-sm">{item.name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MessageBubble({ message, onAction, onRetry, retryDisabled }) {
  const isUser = message.role === "user";
  const isError = message.kind === "error";
  return (
    <div
      className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}
    >
      <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
        {isUser ? "You" : "TripMate"}
      </span>
      <div
        role={isError ? "alert" : undefined}
        className={`max-w-[86%] px-4 py-3.5 text-[14.5px] leading-[1.62] ${
          isUser
            ? "rounded-[16px_16px_4px_16px] bg-muted-900 text-white"
            : isError
              ? "rounded-[16px_16px_16px_4px] border border-danger/40 bg-danger-100 text-ink"
              : "rounded-[16px_16px_16px_4px] border border-border bg-inset text-ink"
        }`}
      >
        <p className="m-0 whitespace-pre-line">{message.text}</p>
        {message.itineraryDay && (
          <ItineraryPreview day={message.itineraryDay} />
        )}
        {message.stops?.length > 0 && (
          // Display-only for now: these become real buttons once the
          // Itinerary/Map tabs exist and a stop can be focused there.
          <div className="mt-3 flex flex-wrap gap-1.5">
            {message.stops.map((stop) => (
              <span
                key={stop}
                className="rounded-pill bg-success-100 px-2.5 py-1 text-caption font-medium text-success-700"
              >
                {stop}
              </span>
            ))}
          </div>
        )}
      </div>
      {message.retryText && (
        <button
          type="button"
          onClick={() => onRetry(message.retryText)}
          disabled={retryDisabled}
          className="rounded-pill bg-accent-100 px-3.25 py-1.75 text-[13px] font-medium text-accent-700 disabled:cursor-not-allowed disabled:opacity-45"
        >
          Retry
        </button>
      )}
      {message.actions?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {message.actions.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => onAction(action)}
              className="rounded-pill bg-accent-100 px-3.25 py-1.75 text-[13px] font-medium text-accent-700"
            >
              {action}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div
      className="flex items-center gap-2.5 text-body-sm text-muted-600"
      role="status"
    >
      <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />
      <span>TripMate is thinking…</span>
    </div>
  );
}

function SuggestionChip({ label, onClick, disabled }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control disabled:cursor-not-allowed disabled:opacity-45"
    >
      {label}
    </button>
  );
}

// `onPlan(itinerary)` is called whenever a reply carries an itinerary, so the
// page can hand it to the tabs. Remount (change `key`) to start a new trip.
function ChatPanel({ onPlan }) {
  const { clearSession } = useAuth();
  const [messages, setMessages] = useState(WELCOME_MESSAGES);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  // Planning-session id from ChatResponse.session.id. Null until the first
  // reply; after that it is sent back so messages continue the same session.
  // Plain state on purpose: the backend can't reload a past session yet, so a
  // page refresh starts a new one.
  const [sessionId, setSessionId] = useState(null);
  const mounted = useRef(true);
  // Set synchronously so a fast double Enter or click can't send twice before
  // the `thinking` state has re-rendered.
  const busy = useRef(false);
  const nextId = useRef(0);
  const wasThinking = useRef(false);
  const listEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  // Lets an in-flight reply be dropped if the page unmounts before it lands.
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  // Grows with the text (up to a limit) so Shift+Enter lines stay visible.
  useEffect(() => {
    const field = inputRef.current;
    if (!field) return;
    field.style.height = "auto";
    field.style.height = `${Math.min(field.scrollHeight, MAX_INPUT_HEIGHT_PX)}px`;
  }, [input]);

  // The field is disabled while waiting; give focus back when the reply lands.
  useEffect(() => {
    if (wasThinking.current && !thinking) inputRef.current?.focus();
    wasThinking.current = thinking;
  }, [thinking]);

  const canSend = input.trim().length > 0 && !thinking;

  const makeId = (prefix) => `${prefix}-${nextId.current++}`;

  // Sends `text` and appends TripMate's reply, or an error message with a Retry
  // button. The caller has already put the user's message in the chat.
  const deliver = async (text) => {
    busy.current = true;
    setThinking(true);
    try {
      const response = await sendChatMessage(text, sessionId);
      if (!mounted.current) return;
      if (response.session?.id) {
        setSessionId((current) => current ?? response.session.id);
      }
      // A clarifying question or a failed plan returns itinerary: null; keep
      // whatever itinerary was already showing in that case.
      if (response.itinerary) onPlan(response.itinerary);
      setMessages((prev) => [
        ...prev,
        {
          id: makeId("a"),
          role: "assistant",
          text: response.assistant_message,
        },
      ]);
    } catch (err) {
      if (!mounted.current) return;
      const failure = describeChatError(err);
      if (failure.kind === "auth") {
        // The session is gone and the shared client already tried to refresh
        // it once: clearing it makes ProtectedRoute send the user to /login.
        clearSession();
        return;
      }
      if (failure.resetSession) setSessionId(null);
      setMessages((prev) => [
        ...prev,
        {
          id: makeId("e"),
          role: "assistant",
          kind: "error",
          text: failure.text,
          // Only a retryable error offers Retry, which resends this same text.
          retryText: failure.retryable ? text : null,
        },
      ]);
    } finally {
      busy.current = false;
      if (mounted.current) setThinking(false);
    }
  };

  const sendMessage = (raw) => {
    const text = raw.trim();
    if (!text || busy.current) return;
    setMessages((prev) => [
      // A new message replaces any earlier error (and its Retry button).
      ...prev.filter((message) => message.kind !== "error"),
      { id: makeId("u"), role: "user", text },
    ]);
    setInput("");
    deliver(text);
  };

  // Retry resends the same text without adding the user's message again.
  const retry = (text) => {
    if (busy.current) return;
    setMessages((prev) => prev.filter((message) => message.kind !== "error"));
    deliver(text);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    sendMessage(input);
  };

  // Enter sends; Shift+Enter inserts a new line.
  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent?.isComposing
    ) {
      event.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <section
      aria-label="Trip planning chat"
      className="flex min-h-0 flex-col overflow-hidden rounded-panel bg-surface shadow-control"
    >
      <div className="flex min-h-0 flex-1 flex-col gap-4.5 overflow-y-auto p-5.5">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onAction={setInput}
            onRetry={retry}
            retryDisabled={thinking}
          />
        ))}
        {thinking && <TypingIndicator />}
        <div ref={listEndRef} />
      </div>

      <div className="flex flex-col gap-3 border-t border-divider p-4">
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((label) => (
            <SuggestionChip
              key={label}
              label={label}
              disabled={thinking}
              onClick={() => sendMessage(label)}
            />
          ))}
        </div>
        <form onSubmit={handleSubmit} className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={thinking}
            placeholder="Ask for a change — 'swap Day 3 for something quieter'"
            aria-label="Message"
            className="min-h-10 flex-1 resize-none rounded-card border border-border bg-surface px-4 py-2.5 text-sm text-ink shadow-inset outline-none disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={!canSend}
            aria-label="Send message"
            className="flex h-9.5 w-9.5 flex-none items-center justify-center rounded-full bg-accent text-white disabled:cursor-not-allowed disabled:bg-muted-400"
          >
            <SendHorizontal size={16} aria-hidden="true" />
          </button>
        </form>
      </div>
    </section>
  );
}

export default ChatPanel;
