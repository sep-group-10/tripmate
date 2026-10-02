import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import FormInput from "../components/FormInput";
import Modal from "../components/Modal";
import Button from "../components/Button";
import SectionCard from "../components/SectionCard";
import ChoiceChip from "../components/ChoiceChip";
import SavedMessage from "../components/SavedMessage";
import PasswordChangeForm from "../components/PasswordChangeForm";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { validateFullName } from "../utils/validation";
import { useAuth } from "../hooks/useAuth";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

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

// Travel preferences are stored on the authenticated user profile.
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

function ProfilePage() {
  const { login, clearSession } = useAuth();
  const navigate = useNavigate();

  // Profile information and travel preferences come from GET /users/me.
  const [email, setEmail] = useState("");
  const [loginProvider, setLoginProvider] = useState("local");
  const [profilePictureUrl, setProfilePictureUrl] = useState(null);
  const [loadStatus, setLoadStatus] = useState("loading"); // loading | ready | error
  const [loadError, setLoadError] = useState("");

  const photoInputRef = useRef(null);
  const [photoStatus, setPhotoStatus] = useState("idle"); // idle | uploading | removing | error
  const [photoError, setPhotoError] = useState("");

  const {
    values: personalValues,
    errors: personalErrors,
    setValues: setPersonalValues,
    setErrors: setPersonalErrors,
    handleChange: handlePersonalChange,
    handleBlur: handlePersonalBlur,
    validateAll: validatePersonalAll,
  } = useFormValidation({ fullName: "" }, personalValidators);
  const [savedProfile, flashProfile] = useFlash();
  const [saveStatus, setSaveStatus] = useState("idle"); // idle | saving | error
  const [saveError, setSaveError] = useState("");

  const [budget, setBudget] = useState("Moderate");
  const [pace, setPace] = useState("Relaxed");
  const [interests, setInterests] = useState(["Culture", "Nature", "Food"]);
  const [savedPrefs, flashPrefs] = useFlash();
  const [prefsSaveStatus, setPrefsSaveStatus] = useState("idle");
  const [prefsSaveError, setPrefsSaveError] = useState("");

  useEffect(() => {
    let cancelled = false;
    api
      .get("/api/v1/users/me")
      .then((response) => {
        if (cancelled) return;
        const me = response.data.data;
        setPersonalValues({ fullName: me.full_name });
        setEmail(me.email);
        setLoginProvider(me.login_provider);
        setProfilePictureUrl(me.profile_picture_url);
        setBudget(me.typical_budget_range || "Moderate");
        setPace(me.preferred_pace || "Relaxed");
        setInterests(me.interests || ["Culture", "Nature", "Food"]);
        setLoadStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        const { code, message } = parseApiError(error);
        if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
          clearSession();
          return;
        }
        setLoadError(message);
        setLoadStatus("error");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSaveProfile = async (event) => {
    event.preventDefault();
    const newErrors = validatePersonalAll();
    if (hasErrors(newErrors)) return;

    setSaveStatus("saving");
    setSaveError("");
    try {
      const response = await api.put("/api/v1/users/me", {
        full_name: personalValues.fullName.trim(),
      });
      login(response.data.data);
      flashProfile();
      setSaveStatus("idle");
    } catch (error) {
      const { code, message, details } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        clearSession();
        return;
      }
      if (code === "VALIDATION_ERROR" && details.length > 0) {
        const fieldErrors = {};
        for (const detail of details) {
          fieldErrors[
            detail.field === "full_name" ? "fullName" : detail.field
          ] = detail.message;
        }
        setPersonalErrors((prev) => ({ ...prev, ...fieldErrors }));
      } else {
        setSaveError(message);
      }
      setSaveStatus("error");
    }
  };

  const handlePhotoChange = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setPhotoStatus("uploading");
    setPhotoError("");
    try {
      const response = await api.post(
        "/api/v1/users/me/profile-picture",
        (() => {
          const formData = new FormData();
          formData.append("file", file);
          return formData;
        })(),
      );
      setProfilePictureUrl(response.data.data.profile_picture_url);
      setPhotoStatus("idle");
    } catch (error) {
      const { code, message } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        clearSession();
        return;
      }
      setPhotoError(message);
      setPhotoStatus("error");
    }
  };

  const handleRemovePhoto = async () => {
    setPhotoStatus("removing");
    setPhotoError("");
    try {
      const response = await api.delete("/api/v1/users/me/profile-picture");
      setProfilePictureUrl(response.data.data.profile_picture_url);
      setPhotoStatus("idle");
    } catch (error) {
      const { code, message } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        clearSession();
        return;
      }
      setPhotoError(message);
      setPhotoStatus("error");
    }
  };

  const toggleInterest = (label) => {
    setInterests((prev) =>
      prev.includes(label)
        ? prev.filter((item) => item !== label)
        : [...prev, label],
    );
  };

  const handleSavePreferences = async (event) => {
    event.preventDefault();
    setPrefsSaveStatus("saving");
    setPrefsSaveError("");
    try {
      const response = await api.put("/api/v1/users/me", {
        typical_budget_range: budget,
        preferred_pace: pace,
        interests,
      });
      login(response.data.data);
      flashPrefs();
      setPrefsSaveStatus("idle");
    } catch (error) {
      const { code, message } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        clearSession();
        return;
      }
      setPrefsSaveError(message);
      setPrefsSaveStatus("error");
    }
  };

  const [exportStatus, setExportStatus] = useState("idle"); // idle | exporting | error
  const [exportError, setExportError] = useState("");

  const handleExportData = async () => {
    setExportStatus("exporting");
    setExportError("");
    try {
      const response = await api.get("/api/v1/users/me/export");
      const blob = new Blob([JSON.stringify(response.data.data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "tripmate-my-data.json";
      link.click();
      URL.revokeObjectURL(url);
      setExportStatus("idle");
    } catch (error) {
      const { code, message } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        clearSession();
        return;
      }
      setExportError(message);
      setExportStatus("error");
    }
  };

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [deleteStatus, setDeleteStatus] = useState("idle"); // idle | deleting

  const handleDeleteAccount = async () => {
    setDeleteStatus("deleting");
    setDeleteError("");
    try {
      await api.post("/api/v1/auth/delete-account", {
        current_password:
          loginProvider === "google" ? undefined : deletePassword,
      });
      clearSession();
      navigate("/login", { replace: true });
    } catch (error) {
      const { code, message } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        clearSession();
        return;
      }
      setDeleteError(message);
      setDeleteStatus("idle");
    }
  };

  return (
    <div className="font-body bg-bg px-6 py-14 text-ink">
      <div className="mx-auto flex max-w-[840px] flex-col gap-6">
        <header className="mb-2 flex flex-col gap-1.5">
          <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
            TripMate account
          </span>
          <h1 className="font-heading mt-0.5 mb-1.5 text-[34px] font-semibold tracking-tight">
            Profile
          </h1>
          <p className="m-0 text-md text-muted-600">
            Manage your personal information, account settings and travel
            preferences.
          </p>
        </header>

        <SectionCard title="Personal information" badge="Account">
          <div className="flex items-center gap-4">
            {profilePictureUrl ? (
              <img
                src={profilePictureUrl}
                alt=""
                className="h-[60px] w-[60px] flex-none rounded-pill object-cover"
              />
            ) : (
              <span className="flex h-[60px] w-[60px] flex-none items-center justify-center rounded-pill bg-accent-100 text-xl font-semibold tracking-wide text-accent-700">
                {initials(personalValues.fullName)}
              </span>
            )}
            <div className="flex flex-col gap-1.5">
              <div className="flex gap-2">
                <input
                  ref={photoInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handlePhotoChange}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  onClick={() => photoInputRef.current?.click()}
                  disabled={photoStatus === "uploading"}
                  className="px-3.5 py-1.5 text-xs"
                >
                  {photoStatus === "uploading" ? "Uploading…" : "Change photo"}
                </Button>
                {profilePictureUrl && (
                  <Button
                    variant="ghost"
                    onClick={handleRemovePhoto}
                    disabled={photoStatus === "removing"}
                    className="px-3.5 py-1.5 text-xs"
                  >
                    {photoStatus === "removing" ? "Removing…" : "Remove"}
                  </Button>
                )}
              </div>
              <span className="text-helper text-muted-600">
                JPG, PNG, or WebP, up to 8 MB.
              </span>
              {photoError && (
                <span className="text-helper text-danger">{photoError}</span>
              )}
            </div>
          </div>

          {loadStatus === "loading" && (
            <p className="m-0 text-sm text-muted-600">Loading your profile…</p>
          )}

          {loadStatus === "error" && (
            <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
              {loadError}
            </p>
          )}

          {loadStatus === "ready" && (
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
                    value={email}
                    disabled
                    className="opacity-70"
                  />
                  <span className="mt-1.5 block text-helper text-muted-600">
                    Email address cannot be changed.
                  </span>
                </div>
              </div>

              {saveError && (
                <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                  {saveError}
                </p>
              )}

              <div className="flex items-center justify-end gap-3">
                <SavedMessage show={savedProfile} text="Saved" />
                <Button type="submit" disabled={saveStatus === "saving"}>
                  {saveStatus === "saving" ? "Saving…" : "Save changes"}
                </Button>
              </div>
            </form>
          )}
        </SectionCard>

        <SectionCard title="Account settings" badge="Security">
          {loginProvider === "google" ? (
            <p className="m-0 rounded-lg bg-bg px-4 py-3 text-sm text-muted-600">
              You signed in with Google, so there&apos;s no password to update
              here.
            </p>
          ) : (
            <PasswordChangeForm
              onSuccess={(user) => login(user)}
              onSessionExpired={clearSession}
            />
          )}
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

            {prefsSaveError && (
              <p
                className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger"
                role="alert"
              >
                {prefsSaveError}
              </p>
            )}

            <div className="flex items-center justify-end gap-3">
              <SavedMessage show={savedPrefs} text="Preferences saved" />
              <Button
                type="submit"
                disabled={
                  prefsSaveStatus === "saving" || loadStatus !== "ready"
                }
              >
                {prefsSaveStatus === "saving" ? "Saving…" : "Save preferences"}
              </Button>
            </div>
          </form>
        </SectionCard>

        <SectionCard title="Your data" badge="Privacy">
          <div className="flex items-center justify-between gap-6">
            <div>
              <div className="text-sm font-medium">Export your data</div>
              <div className="text-helper text-muted-600">
                Download everything TripMate holds about your account as a JSON
                file.
              </div>
            </div>
            <Button
              variant="outline"
              onClick={handleExportData}
              disabled={exportStatus === "exporting"}
              className="px-4 py-2"
            >
              {exportStatus === "exporting" ? "Preparing…" : "Export data"}
            </Button>
          </div>
          {exportStatus === "error" && (
            <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
              {exportError}
            </p>
          )}

          <div className="flex items-center justify-between gap-6 border-t border-divider pt-6">
            <div>
              <div className="text-sm font-medium text-danger">
                Delete account
              </div>
              <div className="text-helper text-muted-600">
                Permanently deactivates your account. This cannot be undone.
              </div>
            </div>
            <Button
              variant="dangerOutline"
              onClick={() => setShowDeleteModal(true)}
              className="px-4 py-2"
            >
              Delete account
            </Button>
          </div>
        </SectionCard>
      </div>

      {showDeleteModal && (
        <Modal
          title="Delete your account?"
          subtitle="This action cannot be undone."
          onClose={() => {
            setShowDeleteModal(false);
            setDeletePassword("");
            setDeleteError("");
          }}
          footer={
            <>
              <Button
                variant="outline"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeletePassword("");
                  setDeleteError("");
                }}
                disabled={deleteStatus === "deleting"}
                className="px-4 py-2"
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDeleteAccount}
                disabled={
                  deleteStatus === "deleting" ||
                  (loginProvider !== "google" && !deletePassword)
                }
                className="px-4 py-2"
              >
                {deleteStatus === "deleting" ? "Deleting…" : "Delete account"}
              </Button>
            </>
          }
        >
          {deleteError && (
            <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
              {deleteError}
            </p>
          )}
          {loginProvider === "google" ? (
            <p className="m-0 text-sm text-muted-600">
              Your account was signed in with Google. Confirm below to
              permanently deactivate it.
            </p>
          ) : (
            <FormInput
              id="deletePassword"
              label="Enter your password to confirm"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              value={deletePassword}
              onChange={(event) => setDeletePassword(event.target.value)}
            />
          )}
        </Modal>
      )}
    </div>
  );
}

export default ProfilePage;
