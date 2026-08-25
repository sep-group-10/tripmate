const STORAGE_KEY = "tripmate_profile";

export const defaultProfile = {
  fullName: "Alex Jordan",
  email: "alex@example.com",
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
