import { useEffect, useRef, useState } from "react";
import { SendHorizontal } from "lucide-react";
import { DUMMY_REPLIES, INITIAL_MESSAGES } from "../../data/tripPlanDummyData";

const SUGGESTIONS = ["Swap a day", "Cut LKR 10,000", "Add a tea estate visit"];

const REPLY_DELAY_MS = 1000;

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

function MessageBubble({ message, onAction }) {
  const isUser = message.role === "user";
  return (
    <div
      className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}
    >
      <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
        {isUser ? "You" : "TripMate"}
      </span>
      <div
        className={`max-w-[86%] px-4 py-3.5 text-[14.5px] leading-[1.62] ${
          isUser
            ? "rounded-[16px_16px_4px_16px] bg-muted-900 text-white"
            : "rounded-[16px_16px_16px_4px] border border-border bg-inset text-ink"
        }`}
      >
        <p className="m-0">{message.text}</p>
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

function SuggestionChip({ label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control"
    >
      {label}
    </button>
  );
}

function ChatPanel() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  // Planning-session id. Nothing sets it from a real reply yet; it will be set
  // from ChatResponse.session.id on the first real reply, then sent back so
  // later messages continue the same session.
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const mounted = useRef(true);
  const replyCount = useRef(0);
  const listEndRef = useRef(null);

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

  const canSend = input.trim().length > 0 && !thinking;

  // AI INTEGRATION POINT. Replace this function's body with a real POST to
  // /api/v1/chat (or /api/v1/chat/{session_id} for a continuing session) once
  // the backend planner is ready. See backend/app/schemas/chat.py for the real
  // ChatResponse shape this page's message data already mirrors. It should
  // resolve with a ChatResponse ({ assistant_message, session, itinerary })
  // and reject on failure. The dummy ignores both arguments.
  // eslint-disable-next-line no-unused-vars
  const requestAssistantReply = (text, currentSessionId) =>
    new Promise((resolve) => {
      setTimeout(() => {
        const reply = DUMMY_REPLIES[replyCount.current % DUMMY_REPLIES.length];
        replyCount.current += 1;
        resolve({ assistant_message: reply, session: null, itinerary: null });
      }, REPLY_DELAY_MS);
    });

  const handleSend = async (event) => {
    event.preventDefault();
    if (!canSend) return;

    const text = input.trim();
    setMessages((prev) => [
      ...prev,
      { id: `u-${Date.now()}`, role: "user", text },
    ]);
    setInput("");
    setError(null);
    setThinking(true);

    try {
      const response = await requestAssistantReply(text, sessionId);
      if (!mounted.current) return;
      if (response.session?.id) setSessionId(response.session.id);
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          text: response.assistant_message,
        },
      ]);
    } catch {
      // Unreachable today (the dummy never rejects); this is where a failed
      // real call lands so the thinking indicator can't get stuck.
      if (!mounted.current) return;
      setError("Something went wrong — try again");
    } finally {
      if (mounted.current) setThinking(false);
    }
  };

  return (
    <section
      aria-label="Trip planning chat"
      className="flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-surface shadow-control"
    >
      <div className="flex min-h-0 flex-1 flex-col gap-4.5 overflow-y-auto p-5.5">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onAction={setInput}
          />
        ))}
        {thinking && <TypingIndicator />}
        {error && (
          <p role="alert" className="m-0 text-body-sm text-danger">
            {error}
          </p>
        )}
        <div ref={listEndRef} />
      </div>

      <div className="flex flex-col gap-3 border-t border-divider p-4">
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((label) => (
            <SuggestionChip
              key={label}
              label={label}
              onClick={() => setInput(label)}
            />
          ))}
        </div>
        <form onSubmit={handleSend} className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask for a change — 'swap Day 3 for something quieter'"
            aria-label="Message"
            className="min-h-10 flex-1 rounded-pill border border-border bg-surface px-4 py-2 text-sm text-ink shadow-inset outline-none"
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
