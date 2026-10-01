import { DEMO_ITINERARY } from "../data/tripPlanDummyData";

// DEV-ONLY mock of POST /api/v1/chat, enabled with VITE_USE_MOCK_CHAT=true (see
// chatService.js). It answers in the same shape as the real endpoint. A message
// containing the word "fail" returns an error response instead, so the error
// and Retry path can be tested without a broken backend.
// TODO: the real endpoint is POST /api/v1/chat and /api/v1/chat/{session_id}.

const REPLY_DELAY_MS = 1000;

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Shaped like the error axios rejects with for a failed API response, so the
// UI handles it exactly as it would a real one.
function mockFailure() {
  const error = new Error("Request failed with status code 503");
  error.response = {
    status: 503,
    data: {
      success: false,
      error: {
        code: "EXTERNAL_SERVICE_UNAVAILABLE",
        message: "The planner is temporarily unavailable.",
        details: [],
      },
    },
  };
  return error;
}

function session(id, status, progress) {
  return {
    id,
    status,
    iteration_count: 0,
    progress_message: null,
    progress_percentage: progress,
  };
}

export async function mockSendChatMessage(message, sessionId) {
  await wait(REPLY_DELAY_MS);
  if (/fail/i.test(message)) throw mockFailure();

  const id = sessionId ?? crypto.randomUUID();
  if (/plan|trip|itinerary/i.test(message)) {
    return {
      assistant_message:
        "Your trip plan is ready.\nI've put together a relaxed hill-country itinerary with food stops and short walks.",
      session: session(id, "completed", 100),
      itinerary: DEMO_ITINERARY,
    };
  }
  return {
    assistant_message:
      "To help me plan your trip, could you tell me when you're travelling, how many people are going and what you enjoy?",
    session: session(id, "pending", 0),
    itinerary: null,
  };
}
