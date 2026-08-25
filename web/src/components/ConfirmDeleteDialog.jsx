import Modal from "./Modal";

/** Confirmation dialog shared by all 4 admin entity lists (C3.4) before a
 * delete actually happens — clicking "Delete" on a card only opens this;
 * the record is removed only if the user confirms here. */
function ConfirmDeleteDialog({ recordName, onConfirm, onClose }) {
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
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm font-medium text-ink shadow-control"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="rounded-full bg-danger px-4 py-2 text-sm font-medium text-white shadow-control hover:opacity-90"
          >
            Delete
          </button>
        </>
      }
    />
  );
}

export default ConfirmDeleteDialog;
