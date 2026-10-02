# Planner chat API: what the web app uses, and what it still needs

The web planner page (`/chat`) talks to the backend chat endpoint. **That endpoint exists** (`backend/app/routers/chat.py`) and works: the web app sends a message and renders the reply. This file records the exact contract the frontend relies on, so it doesn't drift, and lists the backend changes the frontend would benefit from. **Nothing here has been changed in `backend/`.**

The frontend code is `web/src/services/chatService.js` (the call) and `web/src/utils/chatErrors.js` (error handling).

---

## 1. The contract the frontend uses (already implemented)

All responses follow `docs/api-contract.md`: success is `{ "success": true, "data": ... }`, errors are `{ "success": false, "error": { "code", "message", "details"? } }`. Fields are snake_case. The frontend decides what to do from `error.code`, never from the message text.

### Start a planning session

`POST /api/v1/chat`

- **Auth:** the `access_token` cookie (the shared axios client sends cookies; a Bearer token also works).
- **Request body:** `{ "message": "<1-4000 chars, not blank>" }`. No other fields (the schema forbids extras).
- **Success:** `200`, body `{ "success": true, "data": ChatResponse }`.

### Continue a session

`POST /api/v1/chat/{session_id}` with the same body. `session_id` is `data.session.id` from an earlier response. The server keeps the conversation history, so the client sends only the new message.

### `ChatResponse`

```jsonc
{
  "assistant_message": "string",          // TripMate's reply, shown as a chat bubble
  "session": {
    "id": "uuid",                         // send back on the next message
    "status": "pending | completed | ...",
    "iteration_count": 0,
    "progress_message": null,
    "progress_percentage": 0
  },
  "itinerary": null | {                   // null while the planner is still asking questions
    "status": "string",
    "days": [{
      "day_number": 1,
      "date": "2026-10-12",               // YYYY-MM-DD
      "day_type": "arrival",
      "items": [{
        "candidate_id": "uuid",
        "category": "attraction | restaurant | hotel | local_event",
        "name": "Temple of the Sacred Tooth Relic",
        "start_time": "09:00",            // HH:MM
        "end_time": "11:00",
        "latitude": 7.2936,               // optional, used for map pins
        "longitude": 80.6413,
        "duration_minutes": 120,
        "opening_hours": null
      }],
      "hotel_id": "uuid | null",
      "hotel_location": { "latitude": 7.29, "longitude": 80.63 },
      "warnings": [],
      "route_optimization": { "local_distance_km": 1.8 }
    }],
    "hotel_by_destination": { "Kandy": "uuid" },
    "unscheduled": [{ "candidate_id": "uuid", "name": "...", "category": "attraction", "reason": "no day had a fitting, open time slot" }],
    "warnings": []
  }
}
```

### Example: a clarifying question (no itinerary yet)

Request: `{ "message": "Plan a 5-day trip to Kandy and Ella under LKR 150,000" }`

```json
{
  "success": true,
  "data": {
    "assistant_message": "To help me plan your trip, could you tell me when you're travelling and how many people are going?",
    "session": { "id": "22b6a73b-5e35-4e5d-a406-e3cce7b75b51", "status": "pending", "iteration_count": 0, "progress_message": null, "progress_percentage": 0 },
    "itinerary": null
  }
}
```

### Example: a finished plan

```json
{
  "success": true,
  "data": {
    "assistant_message": "Your trip plan is ready.\nDay 1 (2026-10-12): ...",
    "session": { "id": "22b6a73b-5e35-4e5d-a406-e3cce7b75b51", "status": "completed", "iteration_count": 0, "progress_message": null, "progress_percentage": 0 },
    "itinerary": { "status": "partial", "days": [ /* see above */ ], "hotel_by_destination": {}, "unscheduled": [], "warnings": [] }
  }
}
```

### Error responses and what the frontend does

| HTTP | `error.code` | Example | Frontend behaviour |
| --- | --- | --- | --- |
| 401 | `TOKEN_EXPIRED` | `{ "success": false, "error": { "code": "TOKEN_EXPIRED", "message": "Access token has expired" } }` | The shared axios client calls `POST /api/v1/auth/refresh` once and retries. If that fails, the user is sent to `/login`. No chat message. |
| 401 | `UNAUTHORIZED`, `INVALID_REFRESH_TOKEN` | | Same as above. |
| 404 | `NOT_FOUND` | `{ "success": false, "error": { "code": "NOT_FOUND", "message": "Planning session not found" } }` | Forgets the session id. Chat shows "That planning session has expired. Please try again to start a new one." with Retry (which starts a fresh session). |
| 400 | `VALIDATION_ERROR` | blank or over-long message | Chat shows "Sorry, I couldn't process that message. Try rewording it." No Retry (resending the same text would fail again). |
| 429 | `RATE_LIMITED` | | Chat shows a "sending too quickly" message with Retry. |
| 503 | `EXTERNAL_SERVICE_UNAVAILABLE` | the LLM provider is down | Chat shows "Sorry, I couldn't reach the planner. Please try again." with Retry. |
| 500 | `INTERNAL_SERVER_ERROR` | `{ "success": false, "error": { "code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred" } }` | Same message and Retry as 503. |
| none | (network error) | backend down, CORS failure | Same message and Retry. |

In every failure the user's message stays in the chat, the input and Send button are re-enabled, and a "Retry" button resends the same text.

---

## 2. Backend changes that would help (not made; for the backend team)

1. **A qualitative budget crashes `/chat` with a 500.** Sending "...moderate budget" makes the preference step fail with `ValidationError ... budget: Input should be a valid decimal (input_value='moderate')`. `PreferenceResult.budget` (`backend/app/schemas/preference.py`) is `Decimal | None`, but the model returns the word it was given. Users naturally say "moderate", "cheap" or "luxury". Suggest accepting a level and mapping it to a number, or instructing the model to convert it to a number. A numeric budget ("10000 LKR") works.
2. **Use specific error codes for planner failures.** An LLM or provider failure surfaces as a generic `INTERNAL_SERVER_ERROR`. Returning `PLANNING_FAILED` (422, already in `docs/api-contract.md`) or `EXTERNAL_SERVICE_UNAVAILABLE` (503) would let the frontend show better wording. Today it treats all of them as "try again".
3. **Order `itinerary.days[].items` by `start_time`.** When the planner doesn't run `route_optimizer`, the items come back from `scheduling_engine` unsorted (meals first, then attractions), for example 19:00 dinner before a 14:00 attraction. The frontend renders them in the order received, so stops show out of time order. Sorting in the backend fixes the Itinerary tab, the Map pin numbers and the `assistant_message` list at once.
4. **Format of `assistant_message`.** It contains markdown (`* **When are you travelling?**`) and `\n` line breaks. The frontend preserves the line breaks but shows asterisks literally. Please either return plain text or tell us markdown is intended (we'll render it).
5. **Return the trip id.** `PlanningSession.trip_id` exists but isn't in `ChatResponse`. The "Save trip" button needs it to call `POST /api/v1/trips/{id}/save` (not built yet). Suggest adding `session.trip_id` (or `trip_id` next to `session`).
6. **Restore a session after a page refresh.** There is no way to read a session's history or its latest itinerary, so a refresh starts a fresh chat. Suggest `GET /api/v1/chat/{session_id}` returning the messages and the last itinerary, and a session list for the "Recent sessions" sidebar.
7. **`session.iteration_count` and `progress_percentage` are always 0** (even when `status` is `completed`), so a progress bar isn't possible. The request is synchronous (about 10 to 30 seconds for a full plan).
8. **Data the Summary and Budget tabs need** is not in the response: per-item costs, travel legs, day titles, hotel names and prices, a cost breakdown (`cost_estimator` computes it but it isn't returned) and trip summary text. Those tabs show placeholder data until it is.

---

## 3. Dev-only mock mode (frontend)

To work on the chat UI without calling the backend (and without spending LLM credits), run the dev server with:

```
VITE_USE_MOCK_CHAT=true npm run dev
```

The mock (`web/src/services/chatMock.js`) waits about one second and answers in the same shape as the real endpoint. A message containing the word "fail" returns a `503 EXTERNAL_SERVICE_UNAVAILABLE` error response instead, to exercise the error and Retry path. It only runs when `import.meta.env.DEV` is true, so it is not part of production builds. The default (`VITE_USE_MOCK_CHAT=false` in `web/.env.example`) uses the real backend.
