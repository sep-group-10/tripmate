import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, MapPin } from "lucide-react";
import FormInput from "../components/FormInput";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { loginValidators } from "../utils/validation";
import { useAuth } from "../hooks/useAuth";
import { useGoogleSignIn } from "../hooks/useGoogleSignIn";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

const initialFormData = { email: "", password: "" };

function LoginPage() {
  const { values, errors, handleChange, handleBlur, validateAll } =
    useFormValidation(initialFormData, loginValidators);
  const { login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | submitting | error
  const [submitError, setSubmitError] = useState("");
  const [unverifiedEmail, setUnverifiedEmail] = useState("");
  const [resendStatus, setResendStatus] = useState("idle"); // idle | sending | sent
  const googleButtonRef = useRef(null);

  const handleGoogleCredential = async (idToken) => {
    setStatus("submitting");
    setSubmitError("");
    try {
      const response = await api.post("/api/v1/auth/google", {
        id_token: idToken,
      });
      login(response.data.data.user);
      navigate("/profile", { replace: true });
    } catch (error) {
      setSubmitError(parseApiError(error).message);
      setStatus("error");
    }
  };

  useGoogleSignIn(googleButtonRef, handleGoogleCredential);

  const onFieldChange = (field) => (event) => {
    if (status === "error") {
      setStatus("idle");
      setSubmitError("");
      setUnverifiedEmail("");
      setResendStatus("idle");
    }
    handleChange(field)(event);
  };

  const handleResendVerification = async () => {
    setResendStatus("sending");
    try {
      await api.post("/api/v1/auth/resend-verification", {
        email: unverifiedEmail,
      });
    } catch {
      // resend-verification never reveals failure details either way -
      // treat it the same as success from the UI's perspective.
    }
    setResendStatus("sent");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const newErrors = validateAll();
    if (hasErrors(newErrors)) return;

    setStatus("submitting");
    setSubmitError("");
    try {
      const response = await api.post("/api/v1/auth/login", {
        email: values.email.trim(),
        password: values.password,
      });
      login(response.data.data.user);
      navigate("/profile", { replace: true });
    } catch (error) {
      // Covers INVALID_CREDENTIALS, ACCOUNT_DEACTIVATED, and anything else
      // (network error, unexpected server error) with the backend's own
      // message - login intentionally never shows field-specific errors,
      // since email/password ambiguity is deliberate on the backend too
      // (see auth.py: same generic error either way).
      const { code, message } = parseApiError(error);
      if (code === "EMAIL_NOT_VERIFIED") {
        setUnverifiedEmail(values.email.trim());
      }
      setSubmitError(message);
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

        <section className="flex flex-col gap-[22px] rounded-card bg-surface p-8 shadow-card">
          <form
            onSubmit={handleSubmit}
            noValidate
            className="flex flex-col gap-[22px]"
          >
            <div>
              <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                Welcome back
              </h2>
              <p className="mt-1.5 mb-0 text-sm text-muted-600">
                Pick up where your last plan left off.
              </p>
            </div>

            {status === "error" && (
              <div className="flex flex-col gap-2 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                <p className="m-0">{submitError}</p>
                {unverifiedEmail &&
                  (resendStatus === "sent" ? (
                    <p className="m-0 text-success">
                      A new verification email is on its way.
                    </p>
                  ) : (
                    <button
                      type="button"
                      onClick={handleResendVerification}
                      disabled={resendStatus === "sending"}
                      className="self-start font-medium text-accent-700 underline disabled:cursor-not-allowed disabled:opacity-70"
                    >
                      {resendStatus === "sending"
                        ? "Sending…"
                        : "Resend verification email"}
                    </button>
                  ))}
              </div>
            )}

            <div ref={googleButtonRef} className="flex w-full justify-center" />

            <div className="flex items-center gap-3">
              <span className="h-px flex-1 bg-divider" />
              <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-500 uppercase">
                or with email
              </span>
              <span className="h-px flex-1 bg-divider" />
            </div>

            <div className="flex flex-col gap-3.5">
              <FormInput
                id="email"
                label="Email address"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={values.email}
                onChange={onFieldChange("email")}
                onBlur={handleBlur("email")}
                error={errors.email}
              />

              <FormInput
                id="password"
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Your password"
                value={values.password}
                onChange={onFieldChange("password")}
                onBlur={handleBlur("password")}
                error={errors.password}
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

              <Link
                to="/forgot-password"
                className="self-end text-sm text-accent-700"
              >
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={status === "submitting"}
              className="flex w-full items-center justify-center gap-2 rounded-full bg-accent px-6 py-3.5 text-md font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {status === "submitting" ? (
                <>
                  <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/35 border-t-white" />
                  Working…
                </>
              ) : (
                "Log in"
              )}
            </button>

            <p className="m-0 text-center text-sm text-muted-600">
              Don&apos;t have an account?{" "}
              <Link to="/register" className="text-accent-700">
                Register
              </Link>
            </p>
          </form>
        </section>
      </div>
    </div>
  );
}

export default LoginPage;
