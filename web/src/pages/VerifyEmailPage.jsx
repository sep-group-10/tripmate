import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CircleCheck, CircleX, MapPin } from "lucide-react";
import FormInput from "../components/FormInput";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  // verifying | success | error
  const [status, setStatus] = useState(token ? "verifying" : "error");
  const [error, setError] = useState(
    token ? "" : "This verification link is missing its token.",
  );

  const [resendEmail, setResendEmail] = useState("");
  const [resendStatus, setResendStatus] = useState("idle"); // idle | sending | sent

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    api
      .post("/api/v1/auth/verify-email", { token })
      .then(() => {
        if (!cancelled) setStatus("success");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(parseApiError(err).message);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  const handleResend = async (event) => {
    event.preventDefault();
    if (!resendEmail.trim()) return;
    setResendStatus("sending");
    try {
      await api.post("/api/v1/auth/resend-verification", {
        email: resendEmail.trim(),
      });
      setResendStatus("sent");
    } catch {
      // resend-verification never reveals failure details either way -
      // treat it the same as success from the UI's perspective.
      setResendStatus("sent");
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
          {status === "verifying" && (
            <p className="m-0 text-sm text-muted-600">Verifying your email…</p>
          )}

          {status === "success" && (
            <>
              <span className="flex h-12 w-12 items-center justify-center rounded-pill bg-success-100 text-success">
                <CircleCheck size={22} aria-hidden="true" />
              </span>
              <div>
                <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                  Email verified
                </h2>
                <p className="mt-1.5 mb-0 text-sm text-muted-600">
                  Your account is ready. You can log in now.
                </p>
              </div>
              <Link
                to="/login"
                className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600"
              >
                Log in
              </Link>
            </>
          )}

          {status === "error" && (
            <>
              <span className="flex h-12 w-12 items-center justify-center rounded-pill bg-danger-100 text-danger">
                <CircleX size={22} aria-hidden="true" />
              </span>
              <div>
                <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
                  Verification failed
                </h2>
                <p className="mt-1.5 mb-0 text-sm text-muted-600">{error}</p>
              </div>

              {resendStatus === "sent" ? (
                <p className="m-0 rounded-lg bg-success-100 px-3 py-2.5 text-sm text-success">
                  If that email has an account, a new link is on its way.
                </p>
              ) : (
                <form
                  onSubmit={handleResend}
                  className="flex w-full flex-col gap-3"
                >
                  <FormInput
                    id="resendEmail"
                    label="Get a new link"
                    type="email"
                    placeholder="you@example.com"
                    value={resendEmail}
                    onChange={(event) => setResendEmail(event.target.value)}
                  />
                  <button
                    type="submit"
                    disabled={resendStatus === "sending"}
                    className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {resendStatus === "sending" ? "Sending…" : "Resend link"}
                  </button>
                </form>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default VerifyEmailPage;
