# Auth Flow

## Token strategy

We use short-lived access tokens + long-lived refresh tokens.

| Token | Lifespan | Purpose | Storage |
|---|---|---|---|
| Access token | 15 minutes | Sent with every API request | Not persisted server-side |
| Refresh token | 7 days | Used only to get a new access token | Stored in DB (hashed), revocable |

**Why two tokens:** If an access token leaks (XSS, intercepted request, etc.), the damage window is only 15 minutes. The refresh token lives longer but is stored more safely and only talks to one endpoint (`/refresh`).

**Storage by platform:**
- **Web:** both tokens in httpOnly cookies (see Client storage & transport contract below)
- **Flutter (mobile):** Authorization: Bearer header + secure storage on device

**Revocation:** Refresh tokens are stored in the database so they can be invalidated on logout, or manually if a token is suspected compromised.

---

## Registration flow

| Step | What happens |
|---|---|
| 1. Input | User submits: name, email, password |
| 2. Validate | Check email format is valid, password meets rules, all required fields present |
| 3. Check duplicate | Look up email in DB. If it already exists → stop, return error: "email already registered" |
| 4. Create user | Hash password with bcrypt (never store plain text). Save user in DB with role = `Tourist` (default role) |
| 5. Generate tokens | Create access token (15 min) and refresh token (7 days). Save refresh token in DB |
| 6. Response | Return user info (no password) + tokens. Web: set httpOnly cookie. Flutter: return tokens in JSON body |

---

## Password rules

Applies to registration, change-password, and reset-password.

| Rule | Value |
|---|---|
| Minimum length | 8 characters |
| Maximum length | 72 characters (bcrypt's own limit — longer input is silently truncated by bcrypt, which would be a worse bug than just rejecting it) |
| Composition | At least one letter and one digit (Unicode-aware — accented letters and non-ASCII digits count) |

Checked in two places: the frontend (`validation.js`) rejects it before submitting, and the backend (`validate_password_strength` in `security.py`) rejects it again regardless — the frontend check is for a fast error message, not a security boundary, so the backend must never trust it alone. Both checks must stay Unicode-aware together, or the two can disagree on the same password.

---

## Login flow

| Step | What happens |
|---|---|
| 1. Input | User submits: email, password |
| 2. Validate | Check fields are not empty |
| 3. Find user | Look up user by email in DB. If not found → return generic error: "invalid credentials" |
| 4. Check password | Compare submitted password against hashed password using bcrypt compare. If wrong → same generic error: "invalid credentials" |
| 5. Generate tokens | Same as registration: access token (15 min) + refresh token (7 days), refresh token saved in DB |
| 6. Response | Same as registration |

**Security note:** Steps 3 and 4 must return the exact same generic error message ("invalid credentials"). This prevents attackers from probing which emails are registered in the system.

---

## Refresh flow

**Endpoint:** `POST /auth/refresh`

**Request body (mobile only):**

```json
{ "refresh_token": "<refresh_token>" }
```

Web clients send no body at all — the refresh token travels as the httpOnly cookie set on login/register, and the server reads that first. The body field only exists for mobile, which has no cookie to rely on.

**Steps:**

1. Client's access token expires (protected endpoints return `TOKEN_EXPIRED`)
2. Client calls `/auth/refresh` — web sends the request with no body (cookie does the work); mobile sends the refresh token in the body
3. Server reads the refresh token from the cookie if present, falling back to the body otherwise, then verifies the token's signature and expiry, confirms its type is `refresh` (an access token cannot be used here), and checks it against the hash stored for that user in the DB
4. If valid: server issues a **new** access token and a **new** refresh token, and invalidates the old refresh token by overwriting its stored hash (rotation — see below)
5. If invalid, expired, already used, or the account is deactivated: server returns `INVALID_REFRESH_TOKEN` (or `ACCOUNT_DEACTIVATED`) and the client must force a full logout
6. Web: both cookies are updated automatically by the response. Mobile: client stores the new access + refresh tokens and retries the original request

**Response (success):**

```json
{
  "success": true,
  "data": {
    "access_token": "<new_access_token>",
    "refresh_token": "<new_refresh_token>"
  }
}
```

Note: the refresh response does **not** include the user object — the client already has it from login/registration. Mobile still reads `refresh_token` from this body since it has nowhere else to get it; web ignores this field entirely and relies on the `Set-Cookie` header instead.

**Rotation:** every successful refresh invalidates the refresh token that was just used. The previous token cannot be reused, even if it has not yet expired. This means a stolen refresh token stops working the next time the legitimate client refreshes (see api-contract.md §7 for the full rotation contract).

**Web clients** never see either token's value directly — both are silently refreshed by the browser via `Set-Cookie` headers. No web frontend code reads or stores a token at all; it only needs to call `/auth/refresh` (no body) when a request comes back `TOKEN_EXPIRED`, then retry.

**Concurrent refreshes:** if multiple requests hit `TOKEN_EXPIRED` at the same moment (e.g. two components fetching data at once), the client must not fire multiple independent `/auth/refresh` calls — since refresh rotates the token, the first call to complete invalidates the token the second call is still using, and the second call fails with `INVALID_REFRESH_TOKEN`. The web client shares one in-flight refresh call across all simultaneous 401s instead.

**Scope of auto-refresh:** the web client only retries-after-refresh on `401`s from authenticated endpoints (e.g. `/users/me`, `/auth/change-password`). Public auth endpoints — `login`, `register`, `google`, `refresh` itself, `forgot-password`, `reset-password`, `verify-email`, `resend-verification` — are excluded, since a `401` from one of these is a real answer (wrong credentials, bad token) and not a sign of an expired session.

---

## Logout & revocation

**Endpoint:** `POST /auth/logout`

**Request body (optional, mobile only):**

```json
{ "refresh_token": "<refresh_token>" }
```

Web sends no body — same cookie-first, body-fallback pattern as `/auth/refresh`.

**Steps:**

1. Server reads the refresh token from the cookie if present, falling back to the body otherwise. If it matches a token currently stored for a user, it is revoked (cleared from the DB) so it can no longer be used at `/auth/refresh`
2. Both cookies (access and refresh) are always cleared on the response, regardless of whether a refresh token was found
3. Logout always returns `200` with `"data": {}` — an unknown, garbage, or already-revoked refresh token does not cause an error, so logout can never be used to probe token validity

Mobile clients should always send their current refresh token on logout so it is properly revoked, not just discarded client-side — otherwise a copy of it (e.g. left in a compromised device's storage) would remain valid until it naturally expires. Web clients get this for free since the cookie is always sent automatically.

---

## Client storage & transport contract

This section defines how each client platform stores tokens and attaches them to API requests. Both platforms must follow this contract so the backend's auth behavior does not need to differ per client.

### Web application

**Both tokens:** stored in **httpOnly cookies** (`access_token`, `refresh_token`) set by the server on `/auth/register`, `/auth/login`, and `/auth/refresh`. Both cookies are `HttpOnly`, `SameSite=Lax`, and `Secure` outside local development.

- `localStorage` was considered and rejected for both tokens: it is readable by any JavaScript running on the page, so an XSS vulnerability anywhere in the app would allow direct token theft. An httpOnly cookie cannot be read by JavaScript at all.
- The web frontend does **not** need to manually read, store, or attach either token — the browser automatically includes both cookies on every request to the API's origin. There is no client-side token-handling code required for authenticated requests.
- On a `401`/`TOKEN_EXPIRED` response, the frontend calls `POST /auth/refresh` with no body — the cookie supplies the refresh token — then retries the original request once the refresh succeeds.

### Mobile application (Flutter)

**Both tokens:** stored using `flutter_secure_storage`, which persists to the iOS Keychain or Android Keystore — encrypted, OS-managed storage, not plain-text like `SharedPreferences`.

- After `/auth/register` or `/auth/login`, read `access_token` and `refresh_token` from the JSON response body and write both to secure storage.
- On every API request, read the access token from secure storage and attach it as an `Authorization: Bearer <access_token>` header.
- On a `401 TOKEN_EXPIRED` response, call `/auth/refresh` with the stored refresh token, overwrite both stored tokens with the new pair, then retry the original request.
- On logout, call `/auth/logout` with the stored refresh token, then delete both tokens from secure storage.

### Shared contract

Regardless of platform:

- The `Authorization: Bearer <access_token>` header is always a valid way to authenticate — the backend accepts it identically to the cookie, checking the header first and falling back to the cookie if absent. This is what makes the mobile flow work without cookies at all.
- `refresh_token` is only ever sent to `/auth/refresh` and `/auth/logout` — as a cookie for web, as a JSON body field for mobile. It must never be attached to ordinary API requests either way.
- Both platforms receive `access_token` and `refresh_token` in the same response shape from `/auth/register`, `/auth/login`, and `/auth/refresh` — web ignores these fields and relies on the cookies instead; mobile reads and stores them directly.

---

## Rate limiting

| Endpoint | Limit | Key |
|---|---|---|
| `POST /auth/register` | 5 / minute | Client IP |
| `POST /auth/login` | 5 / minute | Client IP |
| `POST /auth/google` | 5 / minute | Client IP |
| `POST /auth/resend-verification` | 5 / minute | Client IP |
| `POST /auth/forgot-password` | 5 / minute | Client IP |
| `POST /auth/reset-password` | 5 / minute | Client IP |

**Why:** without a limit, either endpoint can be scripted — thousands of login attempts per second to guess a password, or thousands of fake registrations to spam the system.

**Why per-IP:** simplest fair key, and doesn't require an existing account. **Known limitation:** several real users behind the same IP (e.g. shared office/campus WiFi) share one limit — a burst of logins from that IP can briefly block an unrelated person on the same network. Accepted for now since the block only lasts one minute; revisit if it causes real friction.

**On exceeding the limit:** `429` with `{"success": false, "error": {"code": "RATE_LIMITED", ...}}` — same response shape as every other error, per api-contract.md.

**Storage:** in-memory (per backend process) via `slowapi`. Resets on restart, and does not share state across multiple backend instances. Fine at current scale; switch to `slowapi`'s Redis-backed storage once Redis is provisioned — a one-line config change, no route code changes needed.

