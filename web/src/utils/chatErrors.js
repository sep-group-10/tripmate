import { parseApiError } from "./apiError";

export const PLANNER_UNREACHABLE_TEXT =
  "Sorry, I couldn't reach the planner. Please try again.";

// Error codes that mean the login session is gone (docs/api-contract.md).
const AUTH_CODES = new Set([
  "TOKEN_EXPIRED",
  "UNAUTHORIZED",
  "INVALID_REFRESH_TOKEN",
]);

/** Decides what the chat should do about a failed send. Goes by the error
 * `code` from the { success: false, error: { code, message } } envelope, never
 * the message text. Returns:
 *   kind          "auth" | "session_expired" | "rejected" | "rate_limited" |
 *                 "unavailable"
 *   text          what TripMate says in the chat
 *   retryable     whether to offer a Retry button
 *   resetSession  whether to forget the planning session id
 * An "auth" failure shows no message: the caller should send the user to /login
 * (the shared axios client has already tried to refresh the token once). */
export function describeChatError(error) {
  const { code } = parseApiError(error);

  if (AUTH_CODES.has(code) || error?.response?.status === 401) {
    return { kind: "auth", text: "", retryable: false, resetSession: false };
  }
  if (code === "NOT_FOUND") {
    return {
      kind: "session_expired",
      text: "That planning session has expired. Please try again to start a new one.",
      retryable: true,
      resetSession: true,
    };
  }
  if (code === "VALIDATION_ERROR") {
    return {
      kind: "rejected",
      text: "Sorry, I couldn't process that message. Try rewording it.",
      retryable: false,
      resetSession: false,
    };
  }
  if (code === "RATE_LIMITED") {
    return {
      kind: "rate_limited",
      text: "You're sending messages too quickly. Please wait a moment and try again.",
      retryable: true,
      resetSession: false,
    };
  }
  // Network failure, 5xx, EXTERNAL_SERVICE_UNAVAILABLE, INTERNAL_SERVER_ERROR...
  return {
    kind: "unavailable",
    text: PLANNER_UNREACHABLE_TEXT,
    retryable: true,
    resetSession: false,
  };
}
