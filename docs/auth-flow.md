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

## Refresh flow (summary)

1. Client's access token expires (API returns 401)
2. Client calls `/refresh` with the refresh token
3. Server checks refresh token is valid and not revoked in DB
4. Server issues a new access token
5. Client retries the original request

*Detailed refresh endpoint contract to be finalized when we write API endpoint docs.*

---

