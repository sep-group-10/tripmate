import { X } from "lucide-react";

function Modal({ title, subtitle, onClose, children, footer }) {
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-ink/30 p-8">
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="flex max-h-[88vh] w-[560px] max-w-full flex-col overflow-auto rounded-card bg-surface shadow-card"
      >
        <div className="flex items-start gap-4 border-b border-divider px-6 py-5">
          <div className="flex flex-1 flex-col gap-1">
            <h2 className="font-heading m-0 text-[19px] font-semibold tracking-tight">
              {title}
            </h2>
            {subtitle && (
              <p className="m-0 text-label text-muted-600">{subtitle}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 flex-none items-center justify-center rounded-full text-muted-600"
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>

        <div className="flex flex-col gap-4 px-6 py-5">{children}</div>

        {footer && (
          <div className="flex justify-end gap-2.5 border-t border-divider px-6 py-4.5">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

export default Modal;
