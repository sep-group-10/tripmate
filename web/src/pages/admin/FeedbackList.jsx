import { useEffect, useMemo, useState } from "react";
import { Star, Trash2 } from "lucide-react";
import Modal from "../../components/Modal";
import SearchInput from "../../components/SearchInput";
import { useAuth } from "../../hooks/useAuth";
import {
  listFeedback,
  resolveFeedback,
  reopenFeedback,
  deleteFeedback,
} from "../../services/adminApi";
import { parseApiError } from "../../utils/apiError";

const TABS = [
  { key: "pending", label: "Pending" },
  { key: "resolved", label: "Resolved" },
  { key: "all", label: "All" },
];

const OUTCOMES = ["Fixed the data", "Shared with team", "No action needed"];

function initials(name) {
  const trimmed = (name ?? "").trim();
  if (!trimmed) return "?";
  return trimmed
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function Stars({ rating, size = 14 }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          size={size}
          aria-hidden="true"
          className={i <= rating ? "fill-ink text-ink" : "text-muted-400"}
        />
      ))}
    </span>
  );
}

function StatusPill({ status }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
        status === "pending"
          ? "bg-warn-100 text-warn"
          : "bg-success-100 text-success"
      }`}
    >
      {status === "pending" ? "Pending" : "Resolved"}
    </span>
  );
}

function ConfirmDeleteFeedbackDialog({
  feedback,
  onConfirm,
  onClose,
  submitting,
  submitError,
}) {
  return (
    <Modal
      title="Delete this feedback?"
      subtitle={`${feedback.user_name}'s review will be removed. This can't be undone.`}
      onClose={onClose}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm font-medium text-ink shadow-control disabled:cursor-not-allowed disabled:opacity-70"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={submitting}
            className="rounded-full bg-danger px-4 py-2 text-sm font-medium text-white shadow-control hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {submitting ? "Deleting…" : "Delete"}
          </button>
        </>
      }
    >
      {submitError && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {submitError}
        </p>
      )}
    </Modal>
  );
}

function FeedbackList() {
  const { role } = useAuth();
  const isSuperAdmin = role === "SUPER_ADMIN";

  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const [error, setError] = useState("");
  const [refreshIndex, setRefreshIndex] = useState(0);

  const [tab, setTab] = useState("pending");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  const [outcome, setOutcome] = useState(null);
  const [note, setNote] = useState("");
  const [resolveSubmitting, setResolveSubmitting] = useState(false);
  const [resolveError, setResolveError] = useState("");

  const [reopenSubmitting, setReopenSubmitting] = useState(false);
  const [reopenError, setReopenError] = useState("");

  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  useEffect(() => {
    let cancelled = false;
    listFeedback({})
      .then((data) => {
        if (cancelled) return;
        setItems(data);
        setStatus("ready");
        setSelectedId((current) => {
          if (current && data.some((item) => item.id === current))
            return current;
          const firstPending = data.find((item) => item.status === "pending");
          return (firstPending ?? data[0])?.id ?? null;
        });
      })
      .catch((err) => {
        if (cancelled) return;
        setError(parseApiError(err).message);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [refreshIndex]);

  const pending = useMemo(
    () => items.filter((item) => item.status === "pending"),
    [items],
  );
  const resolved = useMemo(
    () => items.filter((item) => item.status === "resolved"),
    [items],
  );

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items
      .filter((item) => tab === "all" || item.status === tab)
      .filter(
        (item) =>
          !q ||
          [item.user_name, item.comment ?? ""]
            .join(" ")
            .toLowerCase()
            .includes(q),
      );
  }, [items, tab, query]);

  const selected = items.find((item) => item.id === selectedId) ?? null;

  const averageRating = items.length
    ? (
        items.reduce((sum, item) => sum + item.rating, 0) / items.length
      ).toFixed(1)
    : "—";

  const selectRow = (id) => {
    setSelectedId(id);
    setOutcome(null);
    setNote("");
    setResolveError("");
  };

  const handleResolve = async () => {
    if (!outcome || !selected) return;
    setResolveSubmitting(true);
    setResolveError("");
    try {
      await resolveFeedback(selected.id, {
        outcome,
        note: note.trim() || undefined,
      });
      const nextPending = pending.filter((item) => item.id !== selected.id)[0];
      setRefreshIndex((i) => i + 1);
      setSelectedId(nextPending?.id ?? selected.id);
      setOutcome(null);
      setNote("");
    } catch (err) {
      setResolveError(parseApiError(err).message);
    } finally {
      setResolveSubmitting(false);
    }
  };

  const handleSkip = () => {
    if (!selected) return;
    const idx = pending.findIndex((item) => item.id === selected.id);
    const next = pending[(idx + 1) % pending.length];
    if (next) selectRow(next.id);
  };

  const handleReopen = async () => {
    if (!selected) return;
    setReopenSubmitting(true);
    setReopenError("");
    try {
      await reopenFeedback(selected.id);
      setRefreshIndex((i) => i + 1);
    } catch (err) {
      setReopenError(parseApiError(err).message);
    } finally {
      setReopenSubmitting(false);
    }
  };

  const handleConfirmDelete = async () => {
    setDeleteSubmitting(true);
    setDeleteError("");
    try {
      await deleteFeedback(deleteTarget.id);
      const remaining = visible.filter((item) => item.id !== deleteTarget.id);
      setDeleteTarget(null);
      setSelectedId(remaining[0]?.id ?? null);
      setRefreshIndex((i) => i + 1);
    } catch (err) {
      setDeleteError(parseApiError(err).message);
    } finally {
      setDeleteSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
          Admin · Feedback
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Feedback
        </h1>
      </div>

      <div className="grid grid-cols-1 gap-px overflow-hidden rounded-panel border border-border bg-border sm:grid-cols-3">
        <div className="flex flex-col gap-1 bg-surface p-4">
          <span className="text-xs text-muted-600">Average rating</span>
          <span className="font-heading text-2xl font-semibold tracking-tight">
            {averageRating}
            <span className="ml-1 text-sm font-normal text-muted-600">/ 5</span>
          </span>
        </div>
        <div className="flex flex-col gap-1 bg-surface p-4">
          <span className="text-xs text-muted-600">Waiting for review</span>
          <span className="font-heading text-2xl font-semibold tracking-tight">
            {pending.length}
          </span>
        </div>
        <div className="flex flex-col gap-1 bg-surface p-4">
          <span className="text-xs text-muted-600">Resolved</span>
          <span className="font-heading text-2xl font-semibold tracking-tight">
            {resolved.length}
          </span>
        </div>
      </div>

      {status === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading feedback…</p>
      )}

      {status === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {error}
        </p>
      )}

      {status === "ready" && (
        <div className="flex flex-wrap items-start gap-4">
          <div className="flex min-w-0 flex-1 basis-[360px] flex-col overflow-hidden rounded-panel border border-border bg-surface">
            <div className="flex flex-col gap-2 p-3">
              <SearchInput
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search name or words…"
                className="w-full"
              />
              <div className="flex gap-1 border-b border-divider">
                {TABS.map((t) => {
                  const count =
                    t.key === "pending"
                      ? pending.length
                      : t.key === "resolved"
                        ? resolved.length
                        : items.length;
                  return (
                    <button
                      key={t.key}
                      type="button"
                      onClick={() => setTab(t.key)}
                      aria-selected={tab === t.key}
                      className={`-mb-px border-b-2 px-3 py-2 text-sm ${
                        tab === t.key
                          ? "border-accent font-medium text-ink"
                          : "border-transparent text-muted-600"
                      }`}
                    >
                      {t.label}{" "}
                      <span className="text-xs text-muted-500">{count}</span>
                    </button>
                  );
                })}
              </div>
            </div>
            <div className="flex max-h-[560px] flex-col overflow-auto">
              {visible.map((item) => {
                const isSelected = item.id === selectedId;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => selectRow(item.id)}
                    className={`grid grid-cols-[32px_minmax(0,1fr)] gap-3 border-b border-divider px-4 py-3.5 text-left ${
                      isSelected
                        ? "bg-inset shadow-[inset_3px_0_0_0_var(--color-accent)]"
                        : ""
                    }`}
                  >
                    <span className="flex h-8 w-8 flex-none items-center justify-center rounded-pill bg-muted-200 text-xs font-semibold text-muted-700">
                      {initials(item.user_name)}
                    </span>
                    <span className="flex min-w-0 flex-col gap-1">
                      <span className="flex items-baseline gap-2">
                        <span
                          className={`text-sm ${isSelected ? "font-semibold" : "font-medium"}`}
                        >
                          {item.user_name}
                        </span>
                        <span className="ml-auto text-xs text-muted-500">
                          {formatDate(item.created_at)}
                        </span>
                      </span>
                      <span className="flex items-center gap-2 text-xs">
                        <Stars rating={item.rating} size={12} />
                        {item.status === "pending" && item.rating <= 3 && (
                          <span className="ml-auto rounded-full bg-warn-100 px-2 py-0.5 text-xs font-medium text-warn">
                            Low
                          </span>
                        )}
                        {tab === "all" && item.status === "resolved" && (
                          <span className="ml-auto rounded-full bg-success-100 px-2 py-0.5 text-xs font-medium text-success">
                            Resolved
                          </span>
                        )}
                      </span>
                      <span className="line-clamp-2 text-sm text-muted-600">
                        {item.comment}
                      </span>
                    </span>
                  </button>
                );
              })}
              {visible.length === 0 && (
                <div className="flex flex-col items-center gap-1 px-4 py-10 text-center">
                  <span className="text-sm font-medium">
                    {query
                      ? "No matches"
                      : tab === "pending"
                        ? "Queue is clear"
                        : "Nothing here yet"}
                  </span>
                  <span className="text-sm text-muted-600">
                    {query
                      ? "Try a different name or word."
                      : tab === "pending"
                        ? "Every review has been handled."
                        : "Resolved reviews will show up here."}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="min-w-0 flex-[999] basis-[480px] rounded-panel border border-border bg-surface">
            {selected ? (
              <>
                <div className="flex items-center gap-3 border-b border-divider px-6 py-4">
                  <span className="flex h-10 w-10 flex-none items-center justify-center rounded-pill bg-muted-200 text-sm font-semibold text-muted-700">
                    {initials(selected.user_name)}
                  </span>
                  <span className="font-medium">{selected.user_name}</span>
                  <div className="ml-auto flex items-center gap-2">
                    <StatusPill status={selected.status} />
                    {isSuperAdmin && (
                      <button
                        type="button"
                        onClick={() => {
                          setDeleteError("");
                          setDeleteTarget(selected);
                        }}
                        title="Delete feedback"
                        aria-label="Delete feedback"
                        className="flex h-8 w-8 items-center justify-center rounded-full text-muted-600 hover:bg-muted-200 hover:text-danger"
                      >
                        <Trash2 size={16} aria-hidden="true" />
                      </button>
                    )}
                  </div>
                </div>

                <div className="flex flex-col gap-4 p-6">
                  <div className="flex items-center gap-2 text-sm text-muted-600">
                    <Stars rating={selected.rating} size={16} />
                    <span>{formatDate(selected.created_at)}</span>
                  </div>
                  <p className="m-0 max-w-[62ch] text-lg leading-relaxed">
                    "{selected.comment}"
                  </p>

                  {selected.status === "pending" ? (
                    <div className="flex flex-col gap-3 rounded-lg bg-inset p-4">
                      <div className="flex items-baseline">
                        <b className="text-sm font-medium">
                          How did you handle it?
                        </b>
                        <span className="ml-auto text-xs text-muted-500">
                          {pending.findIndex(
                            (item) => item.id === selected.id,
                          ) + 1}{" "}
                          of {pending.length} waiting
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-4">
                        {OUTCOMES.map((o) => (
                          <label
                            key={o}
                            className="flex items-center gap-2 text-sm"
                          >
                            <input
                              type="radio"
                              name="outcome"
                              checked={outcome === o}
                              onChange={() => setOutcome(o)}
                              className="h-4 w-4 accent-accent"
                            />
                            {o}
                          </label>
                        ))}
                      </div>
                      <textarea
                        value={note}
                        onChange={(event) => setNote(event.target.value)}
                        placeholder="Add a note for the team (optional)"
                        rows={3}
                        className="min-h-18 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink shadow-inset outline-none"
                      />
                      {resolveError && (
                        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                          {resolveError}
                        </p>
                      )}
                      <div className="flex flex-wrap items-center gap-2">
                        <button
                          type="button"
                          onClick={handleResolve}
                          disabled={!outcome || resolveSubmitting}
                          className="rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
                        >
                          {resolveSubmitting ? "Saving…" : "Resolve & next"}
                        </button>
                        <button
                          type="button"
                          onClick={handleSkip}
                          className="rounded-full px-3 py-2 text-sm font-medium text-muted-700 hover:bg-muted-200"
                        >
                          Skip
                        </button>
                        {!outcome && (
                          <span className="ml-auto text-xs text-muted-500">
                            Pick an outcome first
                          </span>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-1.5 rounded-lg bg-inset p-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">
                          {selected.resolution_outcome}
                        </span>
                        <span className="ml-auto text-xs text-muted-500">
                          {selected.resolved_by_name
                            ? `${selected.resolved_by_name} · ${formatDate(selected.resolved_at)}`
                            : formatDate(selected.resolved_at)}
                        </span>
                      </div>
                      {selected.resolution_note && (
                        <span className="text-sm text-muted-600">
                          {selected.resolution_note}
                        </span>
                      )}
                      {reopenError && (
                        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                          {reopenError}
                        </p>
                      )}
                      <div className="pt-1">
                        <button
                          type="button"
                          onClick={handleReopen}
                          disabled={reopenSubmitting}
                          className="rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink shadow-control disabled:cursor-not-allowed disabled:opacity-70"
                        >
                          {reopenSubmitting ? "Reopening…" : "Reopen"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex min-h-[320px] flex-col items-center justify-center gap-1 text-center">
                <span className="font-medium">Nothing selected</span>
                <span className="text-sm text-muted-600">
                  Pick a review from the list.
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {deleteTarget && (
        <ConfirmDeleteFeedbackDialog
          feedback={deleteTarget}
          onConfirm={handleConfirmDelete}
          onClose={() => setDeleteTarget(null)}
          submitting={deleteSubmitting}
          submitError={deleteError}
        />
      )}
    </div>
  );
}

export default FeedbackList;
