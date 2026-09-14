const STORAGE_KEY = "tripmate_profile";

// Personal information (full name, email) now comes from the real
// GET/PUT /api/v1/users/me API - see ProfilePage. This local store only
// backs Account Settings and Travel Preferences, which don't have a full
// real backend contract yet (see ProfilePage's header comment).
export const defaultProfile = {
  emailNotifications: true,
  budget: "Moderate",
  pace: "Relaxed",
  interests: ["Culture", "Nature", "Food"],
};

export function loadProfile() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultProfile;
    return { ...defaultProfile, ...JSON.parse(raw) };
  } catch {
    return defaultProfile;
  }
}

export function saveProfile(partial) {
  const next = { ...loadProfile(), ...partial };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}
