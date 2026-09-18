import { useState } from "react";
import { Link, useLocation, Navigate } from "react-router-dom";
import { MailCheck, MapPin } from "lucide-react";
import api from "../services/api";
import { parseApiError } from "../utils/apiError";

function CheckInboxPage() {
  const location = useLocation();
  const email = location.state?.email;
  const [status, setStatus] = useState("idle"); // idle | sending | sent | error
  const [error, setError] = useState("");

  if (!email) {
    return <Navigate to="/register" replace />;
  }

  const handleResend = async () => {
    setStatus("sending");
    setError("");
    try {
      await api.post("/api/v1/auth/resend-verification", { email });
      setStatus("sent");
    } catch (err) {
      setError(parseApiError(err).message);
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
          <span className="flex h-12 w-12 items-center justify-center rounded-pill bg-accent-100 text-accent-700">
            <MailCheck size={22} aria-hidden="true" />
          </span>

          <div>
            <h2 className="font-heading m-0 text-heading-sm font-semibold tracking-tight">
              Check your inbox
            </h2>
            <p className="mt-1.5 mb-0 text-sm text-muted-600">
              We sent a verification link to <strong>{email}</strong>. Click it
              to activate your account.
            </p>
          </div>

          {status === "sent" && (
            <p className="m-0 rounded-lg bg-success-100 px-3 py-2.5 text-sm text-success">
              A new verification email is on its way.
            </p>
          )}

          {status === "error" && (
            <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
              {error}
            </p>
          )}

          <button
            type="button"
            onClick={handleResend}
            disabled={status === "sending"}
            className="rounded-full border border-border bg-surface px-5 py-2.5 text-sm font-medium text-ink shadow-control disabled:cursor-not-allowed disabled:opacity-70"
          >
            {status === "sending" ? "Sending…" : "Resend email"}
          </button>

          <p className="m-0 text-sm text-muted-600">
            Already verified?{" "}
            <Link to="/login" className="text-accent-700">
              Log in
            </Link>
          </p>
        </section>
      </div>
    </div>
  );
}

export default CheckInboxPage;
