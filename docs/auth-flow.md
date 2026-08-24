# Auth Flow

## Token strategy

We use short-lived access tokens + long-lived refresh tokens.

| Token | Lifespan | Purpose | Storage |
|---|---|---|---|
| Access token | 15 minutes | Sent with every API request | Not persisted server-side |
| Refresh token | 7 days | Used only to get a new access token | Stored in DB, revocable |

**Why two tokens:** If an access token leaks (XSS, intercepted request, etc.), the damage window is only 15 minutes. The refresh token lives longer but is stored more safely and only talks to one endpoint (`/refresh`).

**Storage by platform:**
- **Web:** httpOnly cookie
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

**Request body:**

```json
{ "refresh_token": "<refresh_token>" }
```

**Steps:**

1. Client's access token expires (protected endpoints return `TOKEN_EXPIRED`)
2. Client calls `/auth/refresh` with the refresh token from login/register (or the previous refresh)
3. Server verifies the token's signature and expiry, confirms its type is `refresh` (an access token cannot be used here), and checks it against the hash stored for that user in the DB
4. If valid: server issues a **new** access token and a **new** refresh token, and invalidates the old refresh token by overwriting its stored hash (rotation — see below)
5. If invalid, expired, already used, or the account is deactivated: server returns `INVALID_REFRESH_TOKEN` (or `ACCOUNT_DEACTIVATED`) and the client must force a full logout
6. Client stores the new access + refresh tokens and retries the original request

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

Note: the refresh response does **not** include the user object — the client already has it from login/registration.

**Rotation:** every successful refresh invalidates the refresh token that was just used. The previous token cannot be reused, even if it has not yet expired. This means a stolen refresh token stops working the next time the legitimate client refreshes (see api-contract.md §7 for the full rotation contract).

**Web clients** never see the access token cookie value directly — it is silently refreshed by the browser sending the new `Set-Cookie` header. Web clients still need to read `refresh_token` from the response body and use it for the next `/refresh` call, since the refresh token is never stored in a cookie.

---

## Logout & revocation

**Endpoint:** `POST /auth/logout`

**Request body (optional):**

```json
{ "refresh_token": "<refresh_token>" }
```

**Steps:**

1. If a `refresh_token` is provided and matches a token currently stored for a user, it is revoked (cleared from the DB) so it can no longer be used at `/auth/refresh`
2. The access token cookie is always cleared, regardless of whether a refresh token was provided
3. Logout always returns `200` with `"data": {}` — an unknown, garbage, or already-revoked refresh token does not cause an error, so logout can never be used to probe token validity

Clients should always send their current refresh token on logout so it is properly revoked, not just discarded client-side — otherwise a copy of it (e.g. left in a compromised device's storage) would remain valid until it naturally expires.

---

## Client storage & transport contract

This section defines how each client platform stores tokens and attaches them to API requests. Both platforms must follow this contract so the backend's auth behavior does not need to differ per client.

### Web application

**Access token:** stored in an **httpOnly cookie** set by the server on `/auth/register`, `/auth/login`, and `/auth/refresh`. The cookie is `HttpOnly`, `SameSite=Lax`, and `Secure` outside local development.

- `localStorage` was considered and rejected: it is readable by any JavaScript running on the page, so an XSS vulnerability anywhere in the app would allow direct token theft. An httpOnly cookie cannot be read by JavaScript at all.
- The web frontend does **not** need to manually read or attach the access token — the browser automatically includes the cookie on every request to the API's origin. There is no client-side token-handling code required for authenticated requests.
- The web frontend **does** need to read `refresh_token` from the response body on login/register and hold onto it (in memory, or another non-`localStorage` mechanism decided by the frontend team) in order to call `/auth/refresh` when a request returns `TOKEN_EXPIRED`.

### Mobile application (Flutter)

**Both tokens:** stored using `flutter_secure_storage`, which persists to the iOS Keychain or Android Keystore — encrypted, OS-managed storage, not plain-text like `SharedPreferences`.

- After `/auth/register` or `/auth/login`, read `access_token` and `refresh_token` from the JSON response body and write both to secure storage.
- On every API request, read the access token from secure storage and attach it as an `Authorization: Bearer <access_token>` header.
- On a `401 TOKEN_EXPIRED` response, call `/auth/refresh` with the stored refresh token, overwrite both stored tokens with the new pair, then retry the original request.
- On logout, call `/auth/logout` with the stored refresh token, then delete both tokens from secure storage.

### Shared contract

Regardless of platform:

- The `Authorization: Bearer <access_token>` header is always a valid way to authenticate — the backend accepts it identically to the cookie, checking the header first and falling back to the cookie if absent. This is what makes the mobile flow work without cookies at all.
- `refresh_token` is only ever sent in a JSON request body (`/auth/refresh`, `/auth/logout`) — never as a cookie, never as a header. It must never be attached to ordinary API requests.
- Both platforms receive `access_token` and `refresh_token` in the same response shape from `/auth/register`, `/auth/login`, and `/auth/refresh` — only how each platform chooses to store and transmit them afterward differs.

