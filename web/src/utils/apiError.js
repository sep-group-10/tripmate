// Normalizes an error from a real API call into a consistent shape,
// regardless of whether the server responded with the structured
// {success: false, error: {code, message, details}} envelope (see
// docs/api-contract.md) or the request never reached it at all (backend
// down, network offline, CORS misconfiguration).
export function parseApiError(error) {
  const body = error.response?.data?.error;
  if (body) {
    return {
      code: body.code ?? "UNKNOWN_ERROR",
      message: body.message ?? "Something went wrong. Please try again.",
      details: body.details ?? [],
    };
  }
  return {
    code: "NETWORK_ERROR",
    message:
      "Could not reach the server. Please check your connection and try again.",
    details: [],
  };
}
