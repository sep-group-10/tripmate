import { useState } from "react";
import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";
import FormInput from "../components/FormInput";
import { validateEmail } from "../utils/validation";
import api from "../services/api";

function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [status, setStatus] = useState("idle"); // idle | submitting | sent

  const handleSubmit = async (event) => {
    event.preventDefault();
    const emailError = validateEmail(email);
    if (emailError) {
      setError(emailError);
      return;
    }

    setError("");
    setStatus("submitting");
    try {
      await api.post("/api/v1/auth/forgot-password", { email: email.trim() });
    } catch {
      // forgot-password never reveals failure details either way - the
      // user always sees the same generic "check your inbox" outcome.
    }
    setStatus("sent");
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
          {status === "sent" ? (
            <div className="flex flex-col items-center gap-3 text-center">
              <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                Check your inbox
              </h2>
              <p className="m-0 text-sm text-muted-600">
                If <strong>{email.trim()}</strong> has an account, we sent a
                link to reset the password. It expires in 15 minutes.
              </p>
              <Link to="/login" className="text-sm text-accent-700">
                Back to log in
              </Link>
            </div>
          ) : (
            <form
              onSubmit={handleSubmit}
              noValidate
              className="flex flex-col gap-[22px]"
            >
              <div>
                <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                  Forgot your password?
                </h2>
                <p className="mt-1.5 mb-0 text-sm text-muted-600">
                  Enter your email and we&apos;ll send you a reset link.
                </p>
              </div>

              <FormInput
                id="email"
                label="Email address"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  setError("");
                }}
                error={error}
              />

              <button
                type="submit"
                disabled={status === "submitting"}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-accent px-6 py-3.5 text-md font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {status === "submitting" ? "Sending…" : "Send reset link"}
              </button>

              <p className="m-0 text-center text-sm text-muted-600">
                Remembered it?{" "}
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

export default ForgotPasswordPage;
