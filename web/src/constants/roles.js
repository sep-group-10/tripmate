// Mirrors backend/app/core/roles.py. SUPER_ADMIN inherits ADMIN access;
// ADMIN does not inherit TOURIST, so this is an explicit allow-list.
export const ADMIN_ROLES = ["ADMIN", "SUPER_ADMIN"];

// Pages/actions restricted to Super Admin only (e.g. managing other
// admin accounts) - a plain ADMIN does not inherit this one.
export const SUPER_ADMIN_ROLES = ["SUPER_ADMIN"];
