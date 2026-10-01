import { useState } from "react";
import FormInput from "./FormInput";
import Button from "./Button";
import SavedMessage from "./SavedMessage";
import { validatePassword } from "../utils/validation";
import { parseApiError } from "../utils/apiError";
import api from "../services/api";

function PasswordChangeForm({ onSuccess, onSessionExpired }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [currentPasswordError, setCurrentPasswordError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [confirmPasswordError, setConfirmPasswordError] = useState("");
  const [status, setStatus] = useState("idle"); // idle | saving | error
  const [saved, setSaved] = useState(false);

  const flashSaved = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!currentPassword) {
      setCurrentPasswordError("Enter your current password");
      return;
    }
    const newPasswordError = validatePassword(newPassword);
    if (newPasswordError) {
      setPasswordError(newPasswordError);
      return;
    }
    if (confirmPassword !== newPassword) {
      setConfirmPasswordError("Passwords do not match");
      return;
    }

    setCurrentPasswordError("");
    setPasswordError("");
    setConfirmPasswordError("");
    setStatus("saving");
    try {
      const response = await api.post("/api/v1/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      onSuccess?.(response.data.data.user);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setStatus("idle");
      flashSaved();
    } catch (error) {
      const { code, message, details } = parseApiError(error);
      if (code === "TOKEN_EXPIRED" || code === "UNAUTHORIZED") {
        onSessionExpired?.();
        return;
      }
      if (code === "INVALID_CREDENTIALS") {
        setCurrentPasswordError(message);
      } else if (code === "VALIDATION_ERROR" && details.length > 0) {
        const newPasswordDetail = details.find(
          (detail) => detail.field === "new_password",
        );
        setPasswordError(newPasswordDetail?.message ?? message);
      } else {
        setPasswordError(message);
      }
      setStatus("error");
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-6">
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
            setCurrentPasswordError("");
          }}
          error={currentPasswordError}
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
        <FormInput
          id="confirmPassword"
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          placeholder="Re-enter new password"
          value={confirmPassword}
          onChange={(event) => {
            setConfirmPassword(event.target.value);
            setConfirmPasswordError("");
          }}
          error={confirmPasswordError}
        />
      </div>

      <div className="flex items-center justify-end gap-3">
        <SavedMessage show={saved} text="Password updated" />
        <Button variant="dark" type="submit" disabled={status === "saving"}>
          {status === "saving" ? "Updating…" : "Update password"}
        </Button>
      </div>
    </form>
  );
}

export default PasswordChangeForm;
