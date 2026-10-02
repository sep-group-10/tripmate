import { useEffect, useState } from "react";
import Modal from "../../components/Modal";
import ListPagination from "../../components/ListPagination";
import SearchInput from "../../components/SearchInput";
import EntityFormModal from "../../components/EntityFormModal";
import { useAuth } from "../../hooks/useAuth";
import {
  listAdmins,
  createAdmin,
  updateAdminStatus,
} from "../../services/adminApi";
import { parseApiError } from "../../utils/apiError";

const PAGE_SIZE = 20;

const FORM_FIELDS = [
  {
    name: "full_name",
    label: "Full name",
    type: "text",
    placeholder: "e.g. Priya Wickramasinghe",
    required: true,
  },
  {
    name: "email",
    label: "Email",
    type: "text",
    placeholder: "e.g. priya.w@example.com",
    required: true,
    helperText: "An invite email is sent so they can set their own password.",
  },
];

const ROLE_BADGE_CLASSES = {
  ADMIN: "bg-info-100 text-info",
  SUPER_ADMIN: "bg-accent-100 text-accent-700",
};

function RoleBadge({ role }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ${ROLE_BADGE_CLASSES[role] ?? "bg-muted-200 text-muted-700"}`}
    >
      {role === "SUPER_ADMIN" ? "Super Admin" : "Admin"}
    </span>
  );
}

function StatusBadge({ isActive }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
        isActive ? "bg-success-100 text-success" : "bg-danger-100 text-danger"
      }`}
    >
      {isActive ? "Active" : "Suspended"}
    </span>
  );
}

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

/** Confirmation dialog for activating/deactivating an admin account.
 * Mirrors ConfirmDeleteDialog's shape, but the action is reversible (a
 * toggle, not a delete) so the copy and tone differ. */
function ConfirmStatusDialog({
  admin,
  onConfirm,
  onClose,
  submitting,
  submitError,
}) {
  const willDeactivate = admin.is_active;
  return (
    <Modal
      title={
        willDeactivate
          ? `Deactivate ${admin.full_name}?`
          : `Reactivate ${admin.full_name}?`
      }
      subtitle={
        willDeactivate
          ? "They will immediately lose access to the admin panel. You can reactivate them later."
          : "They will regain access to the admin panel."
      }
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
            className={`rounded-full px-4 py-2 text-sm font-medium text-white shadow-control disabled:cursor-not-allowed disabled:opacity-70 ${
              willDeactivate
                ? "bg-danger hover:opacity-90"
                : "bg-accent hover:bg-accent-600"
            }`}
          >
            {submitting
              ? "Saving…"
              : willDeactivate
                ? "Deactivate"
                : "Reactivate"}
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

function AdminsList() {
  const { user: currentUser } = useAuth();
  const [admins, setAdmins] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const [error, setError] = useState("");
  const [refreshIndex, setRefreshIndex] = useState(0);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const [statusTarget, setStatusTarget] = useState(null);
  const [statusSubmitting, setStatusSubmitting] = useState(false);
  const [statusError, setStatusError] = useState("");

  useEffect(() => {
    let cancelled = false;
    listAdmins({ page, limit: PAGE_SIZE, q: query.trim() || undefined })
      .then((data) => {
        if (cancelled) return;
        setAdmins(data.items);
        setTotal(data.total);
        setStatus("ready");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(parseApiError(err).message);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [page, query, refreshIndex]);

  const handleCreate = async (values) => {
    setFormSubmitting(true);
    setFormError("");
    try {
      await createAdmin({
        full_name: values.full_name.trim(),
        email: values.email.trim(),
      });
      setIsFormOpen(false);
      setPage(1);
      setRefreshIndex((i) => i + 1);
    } catch (err) {
      setFormError(parseApiError(err).message);
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleConfirmStatus = async () => {
    setStatusSubmitting(true);
    setStatusError("");
    try {
      await updateAdminStatus(statusTarget.id, !statusTarget.is_active);
      setStatusTarget(null);
      setRefreshIndex((i) => i + 1);
    } catch (err) {
      setStatusError(parseApiError(err).message);
    } finally {
      setStatusSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div>
        <span className="font-mono text-eyebrow font-medium tracking-widest text-muted-600 uppercase">
          Admin · Admins
        </span>
        <h1 className="font-heading mt-1.5 mb-0 text-heading-md font-semibold tracking-tight">
          Manage admins
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setPage(1);
          }}
          placeholder="Search admins…"
          className="w-search"
        />
        <button
          type="button"
          onClick={() => {
            setFormError("");
            setIsFormOpen(true);
          }}
          className="ml-auto rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
        >
          ＋ Add admin
        </button>
      </div>

      {status === "loading" && (
        <p className="m-0 text-sm text-muted-600">Loading admins…</p>
      )}

      {status === "error" && (
        <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
          {error}
        </p>
      )}

      {status === "ready" && (
        <>
          <div className="overflow-hidden rounded-panel border border-border bg-surface">
            <table className="w-full border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-divider text-xs text-muted-600">
                  <th className="px-4 py-3 font-medium">Admin</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Role</th>
                  <th className="px-4 py-3 font-medium">Added</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {admins.map((admin) => {
                  const isSelf = admin.id === currentUser?.id;
                  const isSuperAdmin = admin.role === "SUPER_ADMIN";
                  const canToggle = !isSelf && !isSuperAdmin;
                  return (
                    <tr
                      key={admin.id}
                      className="border-b border-divider last:border-0"
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2.5">
                          <span className="flex h-8 w-8 flex-none items-center justify-center rounded-pill bg-accent-100 text-xs font-semibold text-accent-700">
                            {initials(admin.full_name)}
                          </span>
                          <span className="font-medium text-ink">
                            {admin.full_name}
                            {isSelf && (
                              <span className="ml-1.5 text-xs text-muted-600">
                                (you)
                              </span>
                            )}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-muted-700">
                        {admin.email}
                      </td>
                      <td className="px-4 py-3">
                        <RoleBadge role={admin.role} />
                      </td>
                      <td className="px-4 py-3 text-muted-700">
                        {formatDate(admin.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge isActive={admin.is_active} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          type="button"
                          onClick={() => {
                            setStatusError("");
                            setStatusTarget(admin);
                          }}
                          disabled={!canToggle}
                          title={
                            isSelf
                              ? "You cannot change your own status"
                              : isSuperAdmin
                                ? "Super admin accounts cannot be changed this way"
                                : undefined
                          }
                          className="rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink shadow-control disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          {admin.is_active ? "Deactivate" : "Reactivate"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {admins.length === 0 && (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-4 py-6 text-center text-muted-600"
                    >
                      No admins found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <ListPagination
            page={page}
            pageSize={PAGE_SIZE}
            total={total}
            onPageChange={setPage}
          />
        </>
      )}

      {isFormOpen && (
        <EntityFormModal
          title="Add admin"
          subtitle="They'll receive an email to set their own password."
          submitLabel="Send invite"
          fields={FORM_FIELDS}
          onSubmit={handleCreate}
          onClose={() => setIsFormOpen(false)}
          submitting={formSubmitting}
          submitError={formError}
        />
      )}

      {statusTarget && (
        <ConfirmStatusDialog
          admin={statusTarget}
          onConfirm={handleConfirmStatus}
          onClose={() => setStatusTarget(null)}
          submitting={statusSubmitting}
          submitError={statusError}
        />
      )}
    </div>
  );
}

export default AdminsList;
