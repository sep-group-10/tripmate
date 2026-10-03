# Roles & Permissions (RBAC)

**Status:** Draft — Sprint 2
**Owner:** Kajatheepan
**Purpose:** Shared reference so there is no ambiguity about who can do what. All endpoints must check against this table.

---

## Roles

| Role | Description |
|---|---|
| Tourist | Normal app user. Plans trips, views tourism data, gives feedback. Default role on registration. |
| Admin | Pure staff account. Only responsible for keeping the tourism database correct — attractions, destinations, transport rates. Does not use tourist-facing features and has no access to users, trips, or roles. |
| Super Admin | Full platform control. Inherits everything Admin can do, plus user management, role assignment, analytics, and data export. |

**Role hierarchy:** Super Admin inherits all Admin rights implicitly. Admin does **not** inherit any Tourist rights — Admin is a separate, isolated staff role, not a "higher" version of Tourist.

---

## Permission table

| # | Action | Tourist | Admin | Super Admin |
|---|---|---|---|---|
| 1 | View attractions/destinations | Allowed | Allowed | Allowed |
| 2 | Create trip/itinerary | Allowed | Denied | Denied |
| 3 | View own trips | Allowed | Denied | Allowed |
| 4 | Edit/delete own trip | Allowed | Denied | Allowed |
| 5 | Submit feedback | Allowed | Denied | Allowed |
| 6 | View all users' trips | Denied | Denied | Allowed |
| 7 | Manage tourism data (add/edit/delete) | Denied | Allowed | Allowed |
| 8 | Manage transport rates | Denied | Allowed | Allowed |
| 9 | Manage users (view/deactivate) | Denied | Denied | Allowed |
| 10 | Assign/change user roles | Denied | Denied | Allowed |
| 11 | View analytics/reports | Denied | Denied | Allowed |
| 12 | Export data/reports | Denied | Denied | Allowed |
| 13 | View/resolve feedback | Denied | Allowed | Allowed |
| 14 | Delete feedback | Denied | Denied | Allowed |

---

## Notes

- Every protected endpoint must check the caller's role against this table before executing the action.
- Row 10 (assign roles) is Super Admin only. If Admin could assign roles, an Admin account could escalate itself or anyone else to Super Admin — a security hole.
- Admin has no read access to trips or users (rows 3, 6, 9) — this is intentional, not an oversight. Admin's scope is strictly tourism data, plus resolving feedback (row 13): most feedback reports a tourism-data problem (e.g. a restaurant's listed hours), so Admin is who actually fixes it. Routing every report through Super Admin first would be slow.
- Row 14 (delete feedback) is Super Admin only. Deleting loses data permanently, so it needs the higher role; resolving (row 13) does not delete anything and is reversible (an entry can be reopened), so it doesn't need the same bar.
