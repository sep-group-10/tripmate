import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, MapPin } from "lucide-react";
import FormInput from "../components/FormInput";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { registerValidators } from "../utils/validation";
import { useAuth } from "../hooks/useAuth";
import { useGoogleSignIn } from "../hooks/useGoogleSignIn";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

const initialFormData = { fullName: "", email: "", password: "" };

// Maps backend/app/schemas/user.py's UserRegisterRequest field names
// (from a VALIDATION_ERROR's details array) to this form's field names.
const FIELD_NAME_MAP = {
  full_name: "fullName",
  email: "email",
  password: "password",
};

function RegisterPage() {
  const { values, errors, setErrors, handleChange, handleBlur, validateAll } =
    useFormValidation(initialFormData, registerValidators);
  const { login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | submitting | error
  const [submitError, setSubmitError] = useState("");
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

  const handleSubmit = async (event) => {
    event.preventDefault();
    const newErrors = validateAll();
    if (hasErrors(newErrors)) return;

    setStatus("submitting");
    setSubmitError("");
    try {
      const email = values.email.trim();
      await api.post("/api/v1/auth/register", {
        full_name: values.fullName.trim(),
        email,
        password: values.password,
      });
      navigate("/check-inbox", { replace: true, state: { email } });
    } catch (error) {
      const { code, message, details } = parseApiError(error);
      if (code === "VALIDATION_ERROR" && details.length > 0) {
        const fieldErrors = {};
        for (const detail of details) {
          fieldErrors[FIELD_NAME_MAP[detail.field] ?? detail.field] =
            detail.message;
        }
        setErrors((prev) => ({ ...prev, ...fieldErrors }));
      } else {
        // Covers EMAIL_ALREADY_EXISTS and anything else (network error,
        // unexpected server error) with the backend's own message.
        setSubmitError(message);
      }
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
                Create your account
              </h2>
              <p className="mt-1.5 mb-0 text-sm text-muted-600">
                Free while you plan your first trip.
              </p>
            </div>

            {submitError && (
              <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                {submitError}
              </p>
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
            </div>

            <div className="flex flex-col gap-3">
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
                  "Create account"
                )}
              </button>
              <p className="m-0 text-helper leading-relaxed text-muted-600">
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
        </section>
      </div>
    </div>
  );
}

export default RegisterPage;
