// Mirrors backend/app/core/roles.py. SUPER_ADMIN inherits ADMIN access;
// ADMIN does not inherit TOURIST, so this is an explicit allow-list.
export const ADMIN_ROLES = ["ADMIN", "SUPER_ADMIN"];
