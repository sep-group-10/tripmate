import { useState } from "react";
import FormInput from "../components/FormInput";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { validateFullName } from "../utils/validation";
import { loadProfile, saveProfile } from "../utils/profileStorage";

const BUDGET_OPTIONS = ["Budget", "Moderate", "Luxury"];
const PACE_OPTIONS = ["Relaxed", "Balanced", "Packed"];
const INTEREST_OPTIONS = [
  "Culture",
  "Nature",
  "Food",
  "Adventure",
  "Relaxation",
  "Nightlife",
];

// Email is deliberately excluded: the real PUT /users/me contract
// (backend/app/schemas/profile.py) only allows full_name and preference
// fields here, with extra="forbid" — sending email would reject the whole
// request. Email is shown read-only for this reason, not as an oversight.
const personalValidators = { fullName: validateFullName };

function useFlash(duration = 2000) {
  const [flashed, setFlashed] = useState(false);
  const flash = () => {
    setFlashed(true);
    setTimeout(() => setFlashed(false), duration);
  };
  return [flashed, flash];
}

function initials(name) {
  return name
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

function SectionCard({ title, badge, children }) {
  return (
    <section className="overflow-hidden rounded-card bg-surface shadow-control">
      <div className="flex items-center justify-between gap-4 border-b border-divider px-7 py-4.5">
        <h2 className="font-heading m-0 text-[17px] font-semibold tracking-tight">
          {title}
        </h2>
        <span className="rounded-badge bg-muted-300 px-2 py-[3px] font-mono text-badge font-medium tracking-wider text-muted-700 uppercase">
          {badge}
        </span>
      </div>
      <div className="flex flex-col gap-6 p-7">{children}</div>
    </section>
  );
}

function ChoiceChip({ label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-3.5 py-1.5 text-xs font-medium ${
        active
          ? "bg-accent-100 text-accent-700"
          : "border border-border bg-surface text-ink shadow-control"
      }`}
    >
      {label}
    </button>
  );
}

function SavedMessage({ show, text }) {
  if (!show) return null;
  return <span className="text-helper text-success">{text}</span>;
}

function ProfilePage() {
  const [profile, setProfile] = useState(() => loadProfile());

  const {
    values: personalValues,
    errors: personalErrors,
    handleChange: handlePersonalChange,
    handleBlur: handlePersonalBlur,
    validateAll: validatePersonalAll,
  } = useFormValidation({ fullName: profile.fullName }, personalValidators);
  const [savedProfile, flashProfile] = useFlash();

  const handleSaveProfile = (event) => {
    event.preventDefault();
    const newErrors = validatePersonalAll();
    if (hasErrors(newErrors)) return;
    setProfile(saveProfile({ fullName: personalValues.fullName }));
    flashProfile();
  };

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [savedPassword, flashPassword] = useFlash();
  const [emailNotifications, setEmailNotifications] = useState(
    profile.emailNotifications,
  );

  const handleUpdatePassword = (event) => {
    event.preventDefault();
    if (!currentPassword) {
      setPasswordError("Enter your current password");
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters");
      return;
    }
    setPasswordError("");
    setCurrentPassword("");
    setNewPassword("");
    flashPassword();
  };

  const handleToggleEmailNotifications = () => {
    const next = saveProfile({ emailNotifications: !emailNotifications });
    setProfile(next);
    setEmailNotifications(next.emailNotifications);
  };

  const [budget, setBudget] = useState(profile.budget);
  const [pace, setPace] = useState(profile.pace);
  const [interests, setInterests] = useState(profile.interests);
  const [savedPrefs, flashPrefs] = useFlash();

  const toggleInterest = (label) => {
    setInterests((prev) =>
      prev.includes(label)
        ? prev.filter((item) => item !== label)
        : [...prev, label],
    );
  };

  const handleSavePreferences = (event) => {
    event.preventDefault();
    setProfile(saveProfile({ budget, pace, interests }));
    flashPrefs();
  };

  return (
    <div className="font-body min-h-screen bg-bg px-6 py-14 text-ink">
      <div className="mx-auto flex max-w-[840px] flex-col gap-6">
        <header className="mb-2 flex flex-wrap items-end justify-between gap-6">
          <div>
            <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
              TripMate account
            </span>
            <h1 className="font-heading mt-2 mb-1.5 text-[34px] font-semibold tracking-tight">
              Profile
            </h1>
            <p className="m-0 text-md text-muted-600">
              Manage your personal information, account settings and travel
              preferences.
            </p>
          </div>
          <span className="rounded-pill bg-success-100 px-2.5 py-1 text-xs font-medium text-success">
            Verified traveller
          </span>
        </header>

        <SectionCard title="Personal information" badge="Account">
          <div className="flex items-center gap-4">
            <span className="flex h-[60px] w-[60px] items-center justify-center rounded-pill bg-accent-100 text-xl font-semibold tracking-wide text-accent-700">
              {initials(personalValues.fullName || profile.fullName)}
            </span>
            <div className="flex flex-col gap-1.5">
              <div className="flex gap-2">
                <button
                  type="button"
                  className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-ink shadow-control"
                >
                  Change photo
                </button>
                <button
                  type="button"
                  className="rounded-full px-3.5 py-1.5 text-xs font-medium text-muted-700"
                >
                  Remove
                </button>
              </div>
              <span className="text-helper text-muted-600">
                JPG or PNG, up to 2 MB.
              </span>
            </div>
          </div>

          <form
            onSubmit={handleSaveProfile}
            noValidate
            className="flex flex-col gap-6"
          >
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormInput
                id="fullName"
                label="Full name"
                type="text"
                value={personalValues.fullName}
                onChange={handlePersonalChange("fullName")}
                onBlur={handlePersonalBlur("fullName")}
                error={personalErrors.fullName}
              />
              <div>
                <FormInput
                  id="email"
                  label="Email address"
                  type="email"
                  value={profile.email}
                  disabled
                  className="opacity-70"
                />
                <span className="mt-1.5 block text-helper text-muted-600">
                  Email address cannot be changed.
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <SavedMessage show={savedProfile} text="Saved" />
              <button
                type="submit"
                className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
              >
                Save changes
              </button>
            </div>
          </form>
        </SectionCard>

        <SectionCard title="Account settings" badge="Security">
          <form
            onSubmit={handleUpdatePassword}
            noValidate
            className="flex flex-col gap-6"
          >
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormInput
                id="currentPassword"
                label="Current password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={currentPassword}
                onChange={(event) => {
                  setCurrentPassword(event.target.value);
                  setPasswordError("");
                }}
              />
              <FormInput
                id="newPassword"
                label="New password"
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={newPassword}
                onChange={(event) => {
                  setNewPassword(event.target.value);
                  setPasswordError("");
                }}
                error={passwordError}
              />
            </div>

            <div className="flex flex-col gap-3.5 rounded-lg bg-bg p-4">
              <div className="flex items-center justify-between gap-6">
                <div>
                  <div className="text-sm font-medium">Email notifications</div>
                  <div className="text-helper text-muted-600">
                    Trip updates, price drops and itinerary reminders
                  </div>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={emailNotifications}
                  onClick={handleToggleEmailNotifications}
                  className={`relative h-[22px] w-[38px] flex-none rounded-pill transition-colors ${
                    emailNotifications ? "bg-accent" : "bg-muted-400"
                  }`}
                >
                  <span
                    className={`absolute top-[3px] h-4 w-4 rounded-full bg-white shadow-control transition-transform ${
                      emailNotifications
                        ? "translate-x-[19px]"
                        : "translate-x-[3px]"
                    }`}
                  />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <SavedMessage show={savedPassword} text="Password updated" />
              <button
                type="submit"
                className="rounded-full bg-muted-900 px-5 py-2.5 text-sm font-medium text-white shadow-control"
              >
                Update password
              </button>
            </div>
          </form>
        </SectionCard>

        <SectionCard title="Travel preferences" badge="Planning">
          <form
            onSubmit={handleSavePreferences}
            className="flex flex-col gap-6"
          >
            <div className="flex flex-col gap-2.5">
              <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
                Budget style
              </span>
              <div className="flex flex-wrap gap-2">
                {BUDGET_OPTIONS.map((option) => (
                  <ChoiceChip
                    key={option}
                    label={option}
                    active={budget === option}
                    onClick={() => setBudget(option)}
                  />
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-2.5">
              <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
                Preferred pace
              </span>
              <div className="flex flex-wrap gap-2">
                {PACE_OPTIONS.map((option) => (
                  <ChoiceChip
                    key={option}
                    label={option}
                    active={pace === option}
                    onClick={() => setPace(option)}
                  />
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-2.5">
              <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
                Interests
              </span>
              <div className="flex flex-wrap gap-2">
                {INTEREST_OPTIONS.map((option) => (
                  <ChoiceChip
                    key={option}
                    label={option}
                    active={interests.includes(option)}
                    onClick={() => toggleInterest(option)}
                  />
                ))}
              </div>
              <span className="text-helper text-muted-600">
                {interests.length} selected — we weight your daily plans towards
                these.
              </span>
            </div>

            <div className="flex items-center justify-end gap-3">
              <SavedMessage show={savedPrefs} text="Preferences saved" />
              <button
                type="submit"
                className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
              >
                Save preferences
              </button>
            </div>
          </form>
        </SectionCard>
      </div>
    </div>
  );
}

export default ProfilePage;
