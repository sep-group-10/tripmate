import { useState } from "react";
import { Link } from "react-router-dom";
import FormInput from "../components/FormInput";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { registerValidators } from "../utils/validation";

const initialFormData = { fullName: "", email: "", password: "" };

function RegisterPage() {
  const { values, errors, handleChange, handleBlur, validateAll, reset } =
    useFormValidation(initialFormData, registerValidators);
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | submitting | success | error
  const [submitError, setSubmitError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const newErrors = validateAll();
    if (hasErrors(newErrors)) return;

    setStatus("submitting");
    setSubmitError("");
    try {
      // UI-only for this issue: no real API call yet (that's C4). The delay
      // keeps the loading state real and testable; the try/catch below is
      // already wired for the real request to drop into later.
      await new Promise((resolve) => setTimeout(resolve, 600));
      console.log("Register form submitted:", values);
      setStatus("success");
    } catch {
      setSubmitError("Something went wrong. Please try again.");
      setStatus("error");
    }
  };

  const handleRegisterAnother = () => {
    reset();
    setShowPassword(false);
    setStatus("idle");
    setSubmitError("");
  };

  return (
    <div className="font-body flex min-h-screen items-center justify-center bg-bg px-6 py-12 text-ink">
      <div className="flex w-full max-w-[460px] flex-col items-stretch gap-6">
        <div className="flex items-center justify-center gap-2.5">
          <span className="flex h-[26px] w-[26px] items-center justify-center rounded-lg bg-accent text-white">
            <svg width="15" height="15" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
              <path d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.41,134.55a8,8,0,0,0,9.18,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Zm0,56a32,32,0,1,1-32,32A32,32,0,0,1,128,72Z" />
            </svg>
          </span>
          <span className="font-heading text-lg font-semibold tracking-tight">TripMate</span>
        </div>

        <section className="flex flex-col gap-[22px] rounded-card bg-surface p-8 shadow-card">
          {status === "success" ? (
            <div className="flex flex-col items-start gap-3.5 py-2">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-success-100 text-success">
                <svg width="22" height="22" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
                  <path d="M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a8,8,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z" />
                </svg>
              </span>
              <h2 className="font-heading m-0 text-2xl font-semibold tracking-tight">Account created</h2>
              <p className="m-0 text-[15px] leading-relaxed text-muted-700">
                Welcome, <strong className="font-medium">{values.fullName}</strong>. This is a
                UI-only demo — your details were logged to the console and no account was
                actually created yet.
              </p>
              <button
                type="button"
                onClick={handleRegisterAnother}
                className="mt-1 rounded-full px-3.5 py-2 text-sm text-muted-700"
              >
                Register another account
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-[22px]">
              <div>
                <h2 className="font-heading m-0 text-[26px] font-semibold tracking-tight">
                  Create your account
                </h2>
                <p className="mt-1.5 mb-0 text-sm text-muted-600">
                  Free while you plan your first trip.
                </p>
              </div>

              {status === "error" && (
                <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                  {submitError}
                </p>
              )}

              <button
                type="button"
                className="flex w-full items-center justify-center gap-2 rounded-full border border-border bg-surface px-[18px] py-[11px] text-sm font-medium text-ink shadow-control"
              >
                <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
                  <path fill="#4285F4" d="M45.1 24.5c0-1.6-.1-2.8-.4-4H24v7.6h12c-.2 2-1.5 5-4.4 7l6.7 5.2c4-3.7 6.8-9.1 6.8-15.8z" />
                  <path fill="#34A853" d="M24 46c6 0 11-2 14.3-5.7l-6.7-5.2c-1.8 1.3-4.3 2.2-7.6 2.2-5.8 0-10.8-3.9-12.6-9.2l-7 5.4C7.8 41 15.3 46 24 46z" />
                  <path fill="#FBBC05" d="M11.4 28.1c-.5-1.4-.8-2.9-.8-4.5s.3-3.1.7-4.5l-7-5.4C2.9 16.8 2 20.3 2 23.6s.9 6.8 2.4 9.9l7-5.4z" />
                  <path fill="#EA4335" d="M24 9.9c4.1 0 6.9 1.8 8.5 3.3l6-5.8C34.9 3.9 30 2 24 2 15.3 2 7.8 7 4.4 13.7l7 5.4C13.2 13.8 18.2 9.9 24 9.9z" />
                </svg>
                Continue with Google
              </button>

              <div className="flex items-center gap-3">
                <span className="h-px flex-1 bg-divider" />
                <span className="font-mono text-[11px] font-medium tracking-widest text-muted-500 uppercase">
                  or with email
                </span>
                <span className="h-px flex-1 bg-divider" />
              </div>

              <div className="flex flex-col gap-3.5">
                <FormInput
                  id="fullName"
                  label="Full name"
                  type="text"
                  autoComplete="name"
                  placeholder="Alex Jordan"
                  value={values.fullName}
                  onChange={handleChange("fullName")}
                  onBlur={handleBlur("fullName")}
                  error={errors.fullName}
                />

                <FormInput
                  id="email"
                  label="Email address"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={values.email}
                  onChange={handleChange("email")}
                  onBlur={handleBlur("email")}
                  error={errors.email}
                />

                <FormInput
                  id="password"
                  label="Password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="At least 8 characters"
                  value={values.password}
                  onChange={handleChange("password")}
                  onBlur={handleBlur("password")}
                  error={errors.password}
                  endAdornment={
                    <button
                      type="button"
                      onClick={() => setShowPassword((prev) => !prev)}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                      className="absolute top-1/2 right-1 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-muted-600"
                    >
                      <svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
                        <path d="M247.31,124.76c-.35-.79-8.82-19.58-27.65-38.41C194.57,61.26,162.88,48,128,48S61.43,61.26,36.34,86.35C17.51,105.18,9,124,8.69,124.76a8,8,0,0,0,0,6.5c.35.79,8.82,19.57,27.65,38.4C61.43,194.74,93.12,208,128,208s66.57-13.26,91.66-38.34c18.83-18.83,27.3-37.61,27.65-38.4A8,8,0,0,0,247.31,124.76ZM128,168a40,40,0,1,1,40-40A40,40,0,0,1,128,168Z" />
                      </svg>
                    </button>
                  }
                />
              </div>

              <div className="flex flex-col gap-3">
                <button
                  type="submit"
                  disabled={status === "submitting"}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-accent px-6 py-3.5 text-[15px] font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {status === "submitting" ? (
                    <>
                      <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/35 border-t-white" />
                      Working…
                    </>
                  ) : (
                    "Create account"
                  )}
                </button>
                <p className="m-0 text-[12.5px] leading-relaxed text-muted-600">
                  By creating an account you agree to our{" "}
                  <a href="#terms" className="text-accent-700">
                    Terms of Service
                  </a>{" "}
                  and{" "}
                  <a href="#privacy" className="text-accent-700">
                    Privacy Policy
                  </a>
                  .
                </p>
              </div>

              <p className="m-0 text-center text-sm text-muted-600">
                Already have an account?{" "}
                <Link to="/login" className="text-accent-700">
                  Log in
                </Link>
              </p>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}

export default RegisterPage;
