import Modal from "./Modal";

/** Confirmation dialog shared by all 4 admin entity lists (C3.4) before a
 * delete actually happens — clicking "Delete" on a card only opens this;
 * the record is removed only if the user confirms here.
 * `submitting`/`submitError` surface the caller's async onConfirm result -
 * this component doesn't call the API itself, so it can't know that state
 * on its own. */
function ConfirmDeleteDialog({
  recordName,
  onConfirm,
  onClose,
  submitting = false,
  submitError = "",
}) {
  return (
    <Modal
      title={`Delete ${recordName}?`}
      subtitle="This action cannot be undone."
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

export default ConfirmDeleteDialog;
