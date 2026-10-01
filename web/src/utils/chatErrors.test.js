import { describe, it, expect } from "vitest";
import { PLANNER_UNREACHABLE_TEXT, describeChatError } from "./chatErrors";

// Shaped like the error axios rejects with for an API error response.
const apiError = (status, code) => {
  const error = new Error(`status ${status}`);
  error.response = {
    status,
    data: { success: false, error: { code, message: "ignored text" } },
  };
  return error;
};

describe("describeChatError", () => {
  it("treats a network failure as retryable planner-unreachable", () => {
    expect(describeChatError(new Error("Network Error"))).toMatchObject({
      kind: "unavailable",
      text: PLANNER_UNREACHABLE_TEXT,
      retryable: true,
    });
  });

  it("treats 5xx and service-unavailable codes the same way", () => {
    for (const [status, code] of [
      [500, "INTERNAL_SERVER_ERROR"],
      [503, "EXTERNAL_SERVICE_UNAVAILABLE"],
    ]) {
      expect(describeChatError(apiError(status, code))).toMatchObject({
        kind: "unavailable",
        retryable: true,
      });
    }
  });

  it("detects a dead login session by code and by 401", () => {
    expect(describeChatError(apiError(401, "TOKEN_EXPIRED")).kind).toBe("auth");
    expect(describeChatError(apiError(401, "INVALID_REFRESH_TOKEN")).kind).toBe(
      "auth",
    );
    expect(describeChatError(apiError(401, "SOMETHING_NEW")).kind).toBe("auth");
  });

  it("resets the session when the planning session is not found", () => {
    expect(describeChatError(apiError(404, "NOT_FOUND"))).toMatchObject({
      kind: "session_expired",
      resetSession: true,
      retryable: true,
    });
  });

  it("does not offer Retry for a message the server rejected", () => {
    expect(describeChatError(apiError(400, "VALIDATION_ERROR"))).toMatchObject({
      kind: "rejected",
      retryable: false,
    });
  });

  it("handles rate limiting", () => {
    expect(describeChatError(apiError(429, "RATE_LIMITED"))).toMatchObject({
      kind: "rate_limited",
      retryable: true,
    });
  });

  it("decides by code, never by the message text", () => {
    const error = apiError(500, "INTERNAL_SERVER_ERROR");
    error.response.data.error.message = "Token expired";
    expect(describeChatError(error).kind).toBe("unavailable");
  });
});
