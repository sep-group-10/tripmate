import api from "./api";

// Dev-only mock of the chat endpoint (see chatMock.js): used when running the
// dev server with VITE_USE_MOCK_CHAT=true. import.meta.env.DEV is false in a
// production build, so the branch below and the mock module are dropped there.
const USE_MOCK =
  import.meta.env.DEV && import.meta.env.VITE_USE_MOCK_CHAT === "true";

/** Sends one user message to the planner and resolves with the ChatResponse
 * ({ assistant_message, session, itinerary }) from the standard
 * { success, data } envelope. Starts a session when `sessionId` is null.
 * Rejects like any axios call; use describeChatError (utils/chatErrors.js).
 * Real endpoints: POST /api/v1/chat and POST /api/v1/chat/{session_id}
 * (backend/app/routers/chat.py, contract in docs/chat-api-needed.md). */
export async function sendChatMessage(message, sessionId) {
  if (USE_MOCK) {
    // TODO: remove the mock once the real endpoint is stable for everyone.
    const { mockSendChatMessage } = await import("./chatMock");
    return mockSendChatMessage(message, sessionId);
  }
  const res = await api.post(
    sessionId ? `/api/v1/chat/${sessionId}` : "/api/v1/chat",
    { message },
  );
  return res.data.data;
}
