# API Contract

This document defines the common API standards followed across the backend, web frontend, mobile application, and other project components of the AI-Powered Smart Tourism Assistant Platform.

Every API in this project must follow the rules in this document. This keeps responses consistent, so any client (web, mobile) can handle them the same way.

---

## 0. Base Rules

**API Versioning**
All endpoints are prefixed with a version number:

```
/api/v1/...
```

Example: `/api/v1/auth/login`, `/api/v1/destinations`

**Authentication Header**
Protected endpoints require the access token sent as a Bearer token in the request header:

```
Authorization: Bearer <access_token>
```

**Field Naming Convention**
All JSON field names (in requests and responses) use snake_case. Example: `access_token`, `created_at`, `total_pages` — not `accessToken` or `createdAt`.

---

## 1. Success Response Format

All successful API responses must follow this structure:

- `success` — always `true`
- `data` — an object containing the response data

```json
{
  "success": true,
  "data": {}
}
```

**HTTP Status Codes for Success**

| Status | Use When |
|---|---|
| 200 OK | Standard successful response (GET, PUT, PATCH, and most POST actions like login) |
| 201 Created | A new resource was created (e.g. register, create destination) |
| 202 Accepted | Request accepted but processing happens asynchronously (e.g. long-running AI planning job, later sprint) |

No 204 No Content in this project. 204 cannot contain a response body, but this contract requires every success response to include `data`. To avoid that conflict, actions with nothing to return (logout, delete) still use 200 with `"data": {}`, never 204.

Example (fetching a user profile):

```json
{
  "success": true,
  "data": {
    "id": "u_123",
    "name": "Kasun Perera",
    "email": "kasun@example.com"
  }
}
```

Actions with no data to return (e.g. logout, delete): always return 200, with `data` as an empty object.

```json
{
  "success": true,
  "data": {}
}
```

---

## 2. Error Response Format

All API errors must follow this structure:

- `success` — always `false`
- `error` — an object containing:
  - `code` — a short, fixed string identifying the error type
  - `message` — a human-readable description of what went wrong

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

**Validation errors — structured field details**

For `VALIDATION_ERROR`, the error object also includes a `details` array, so clients can show which exact fields are wrong (important when multiple fields fail at once):

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Some fields are invalid",
    "details": [
      { "field": "email", "message": "Email format is invalid" },
      { "field": "password", "message": "Password must be at least 8 characters" }
    ]
  }
}
```

For all other error codes, `details` is not required.

**Framework-generated errors**

The backend framework (e.g. Express, Django) may generate its own error responses for things like invalid routes, wrong HTTP methods, or unhandled exceptions. These must be caught and converted into this same `success: false` / `error` format before reaching the client — no raw framework error pages or default error formats should ever be returned.

---

## 3. Standard Error Codes

### 3.1 Active Error Codes (used in current sprints)

| Error Code | HTTP Status | Meaning | When to Return It |
|---|---|---|---|
| VALIDATION_ERROR | 400 | Input data failed validation | A request body/field is missing, malformed, or doesn't meet required rules (e.g. weak password, invalid email format) |
| UNAUTHORIZED | 401 | Request has no valid authentication | No token was sent, or the token is malformed/invalid, but the endpoint requires authentication |
| TOKEN_EXPIRED | 401 | Access token expired | The JWT access token sent with the request is valid but has expired. The client should attempt a token refresh before forcing logout. |
| FORBIDDEN | 403 | Authenticated but not allowed | The user is logged in, but their role (e.g. normal user) does not have permission to perform this action (e.g. accessing an admin-only endpoint) |
| NOT_FOUND | 404 | Resource does not exist | The requested resource (user, destination, hotel, etc.) does not exist in the database |
| EMAIL_ALREADY_EXISTS | 409 | Duplicate registration | A user tries to register with an email address that is already registered |
| INVALID_CREDENTIALS | 401 | Wrong login details | Email/password combination is incorrect during login |
| ACCOUNT_DEACTIVATED | 403 | Account is inactive | A user tries to log in but their account has been deactivated by an admin or the system |
| INVALID_REFRESH_TOKEN | 401 | Refresh token invalid | The refresh token used to get a new access token is invalid, expired, or has already been used. Client must force logout when this occurs. |
| INTERNAL_SERVER_ERROR | 500 | Unexpected server-side failure | Database errors, unhandled exceptions, or any unexpected crash. The client only sees a safe generic message; full technical details go to server logs, never to the client. |
| EXTERNAL_SERVICE_UNAVAILABLE | 503 | Third-party service failure | An external API the system depends on (e.g. weather API, Gemini API, maps API) is unreachable or returns an error |

### 3.2 Reserved Error Codes (for later sprints — documented now, not yet implemented)

| Error Code | HTTP Status | Meaning | Planned For |
|---|---|---|---|
| EMAIL_NOT_VERIFIED | 403 | Email not confirmed | Only relevant if email verification is added to the auth flow. Open question: not currently in the SRS auth flow (register/login/reset/logout only) — confirm with team before implementing. |
| PLANNING_FAILED | 422 | AI trip planning could not complete | AI Travel Planning module (later sprint) |
| EXPORT_FAILED | 500 | Export operation failed | Itinerary/report export, e.g. PDF (later sprint) |
| RATE_LIMITED | 429 | Too many requests | For endpoints that need rate limiting (e.g. login attempts, AI chat requests) — only implement if/when rate limiting is added to the project |

**UNAUTHORIZED vs TOKEN_EXPIRED — the difference:**

- `TOKEN_EXPIRED` is a specific signal: the token was valid but timed out. The client should silently try the refresh-token flow first, without logging the user out.
- `UNAUTHORIZED` is the general case: no token, broken token, or refresh already failed. The client should log the user out and redirect to login.

**Error code compatibility rule:** Clients must check `error.code`, never the message text, to decide how to handle an error (message text can change anytime for wording/translation). Once an error code is in active use, its meaning must not change within the same API version — if the meaning needs to change, introduce a new code instead.

---

## 4. Date and Time Format

Timestamps (a specific moment in time, e.g. `created_at`, `updated_at`) must use ISO 8601 format, in UTC:

```
2026-08-10T22:30:00Z
```

Date-only fields (a calendar day with no specific time, e.g. trip start date, trip end date) must use `YYYY-MM-DD` only, with no time or timezone component:

```
2026-08-10
```

This split matters for a travel app — a trip date is a calendar day regardless of timezone, and attaching a UTC time to it can shift the date by a day depending on where the user is.

**Rules:**

- Always include the time zone indicator (`Z` for UTC) on timestamps.
- Do not use locale-specific formats (e.g. `10/08/2026` or `10-Aug-2026`) anywhere.
- Use timestamps (`created_at`, `updated_at`) vs date-only (trip dates) as described above — don't mix the two.

---

## 5. Pagination Format

All API endpoints that return a list of items must support pagination and follow this structure:

- `items` — array of results for the current page
- `total` — total number of records available
- `page` — current page number
- `limit` — number of items per page
- `total_pages` — total number of pages available

```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "limit": 10,
    "total_pages": 0
  }
}
```

Example (list of destinations):

```json
{
  "success": true,
  "data": {
    "items": [
      { "id": "d_1", "name": "Sigiriya" },
      { "id": "d_2", "name": "Ella" }
    ],
    "total": 42,
    "page": 1,
    "limit": 10,
    "total_pages": 5
  }
}
```

**Pagination request (query parameters)**

Clients request pages using query parameters:

```
GET /api/v1/destinations?page=1&limit=10
```

| Parameter | Default | Rules |
|---|---|---|
| page | 1 | Must be a positive integer. If a client requests a page beyond `total_pages` (e.g. page 999 when only 5 exist), return an empty `items` array with 200, not an error. |
| limit | 10 | Maximum allowed value is 50. If a client requests more than 50, cap it at 50 rather than returning an error. |

`total_pages` is calculated as `ceil(total / limit)`.

---

## 6. Non-JSON Responses (Files)

Some endpoints don't return the standard JSON envelope — for example, PDF exports, image downloads, or file streaming (e.g. exporting an itinerary as a PDF). These return the raw file with the appropriate `Content-Type` header (e.g. `application/pdf`) instead of `{ success, data }`.

If the file generation fails, the error still follows the standard JSON error format (e.g. `EXPORT_FAILED`), since no file exists yet to return at that point.

---

## 7. Refresh Token Behavior

When a client uses a refresh token to get a new access token, the old refresh token is invalidated immediately (rotation). The response includes a new refresh token, which the client must store and use next time.

If an already-used (rotated out) or expired refresh token is sent, the server returns `INVALID_REFRESH_TOKEN`, and the client must force a full logout and redirect to login — it cannot silently retry.

Refresh tokens are only ever sent to the dedicated refresh endpoint, never accepted as authentication on other endpoints (only access tokens are accepted there).

---

## 8. Example Responses (Combined Reference)

Successful login:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "user": {
      "id": "u_123",
      "name": "Kasun Perera",
      "email": "kasun@example.com",
      "role": "user"
    }
  }
}
```

Validation error on registration:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Some fields are invalid",
    "details": [
      { "field": "password", "message": "Password must be at least 8 characters long" }
    ]
  }
}
```

Forbidden access:

```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to access this resource"
  }
}
```
