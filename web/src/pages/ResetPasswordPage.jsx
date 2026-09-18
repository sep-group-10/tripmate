import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CircleCheck, Eye, EyeOff, MapPin } from "lucide-react";
import FormInput from "../components/FormInput";
import { validatePassword } from "../utils/validation";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | submitting | success | error
  const [submitError, setSubmitError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!token) return;

    const validationError = validatePassword(newPassword);
    if (validationError) {
      setPasswordError(validationError);
      return;
    }

    setPasswordError("");
    setSubmitError("");
    setStatus("submitting");
    try {
      await api.post("/api/v1/auth/reset-password", {
        token,
        new_password: newPassword,
      });
      setStatus("success");
    } catch (error) {
      setSubmitError(parseApiError(error).message);
      setStatus("error");
    }
  };

  return (
    <div className="font-body flex min-h-screen items-center justify-center bg-bg px-6 py-12 text-ink">
      <div className="flex w-full max-w-auth-card flex-col items-stretch gap-6">
        <div className="flex items-center justify-center gap-2.5">
          <span className="flex h-logo w-logo items-center justify-center rounded-lg bg-accent text-white">
            <MapPin size={15} aria-hidden="true" />
          </span>
          <span className="font-heading text-lg font-semibold tracking-tight">
            TripMate
          </span>
        </div>

        <section className="flex flex-col items-center gap-4 rounded-card bg-surface p-8 text-center shadow-card">
          {!token ? (
            <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
              This reset link is missing its token.
            </p>
          ) : status === "success" ? (
            <>
              <span className="flex h-12 w-12 items-center justify-center rounded-pill bg-success-100 text-success">
                <CircleCheck size={22} aria-hidden="true" />
              </span>
              <div>
                <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                  Password reset
                </h2>
                <p className="mt-1.5 mb-0 text-sm text-muted-600">
                  You can log in with your new password now.
                </p>
              </div>
              <Link
                to="/login"
                className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600"
              >
                Log in
              </Link>
            </>
          ) : (
            <form
              onSubmit={handleSubmit}
              noValidate
              className="flex w-full flex-col gap-[22px] text-left"
            >
              <div>
                <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                  Choose a new password
                </h2>
              </div>

              {status === "error" && (
                <div className="flex flex-col gap-2 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                  <p className="m-0">{submitError}</p>
                  <Link to="/forgot-password" className="self-start underline">
                    Request a new link
                  </Link>
                </div>
              )}

              <FormInput
                id="newPassword"
                label="New password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={newPassword}
                onChange={(event) => {
                  setNewPassword(event.target.value);
                  setPasswordError("");
                }}
                error={passwordError}
                endAdornment={
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                    className="absolute top-1/2 right-1 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-muted-600"
                  >
                    {showPassword ? (
                      <EyeOff size={16} aria-hidden="true" />
                    ) : (
                      <Eye size={16} aria-hidden="true" />
                    )}
                  </button>
                }
              />

              <button
                type="submit"
                disabled={status === "submitting"}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-accent px-6 py-3.5 text-md font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {status === "submitting" ? "Saving…" : "Reset password"}
              </button>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}

export default ResetPasswordPage;
