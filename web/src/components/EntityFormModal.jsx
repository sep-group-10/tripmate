import { ImagePlus } from "lucide-react";
import Modal from "./Modal";
import FormInput from "./FormInput";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { validateRequired } from "../utils/validation";

const SELECT_CLASSES =
  "min-h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm text-ink shadow-inset outline-none";

const noValidate = () => "";

/** Config-driven "Add/Edit [Entity]" form, shared by all 4 admin entity
 * forms (C3.2/C3.3) instead of near-identical hand-written forms per entity
 * per mode — the entities' fields differ, but the field TYPES
 * (text/select/textarea/number) and the required/optional/validate/submit/
 * cancel plumbing are identical. Each field is { name, label, type:
 * 'text'|'select'|'textarea'|'number', options?, placeholder?, required?,
 * validate? } - `validate` overrides the default required/no-op validator
 * with a custom one (e.g. numeric range checks for lat/long).
 * Pass `initialValues` (an existing record) to open in edit mode — fields
 * are pre-filled and the caller's onSubmit decides whether that means
 * updating that record or creating a new one; this component doesn't know
 * or care which mode it's in beyond what to pre-fill.
 * `submitting`/`submitError` surface the caller's async onSubmit result -
 * this component doesn't call the API itself, so it can't know that state
 * on its own. */
function EntityFormModal({
  title,
  subtitle,
  submitLabel,
  fields,
  initialValues,
  onSubmit,
  onClose,
  submitting = false,
  submitError = "",
}) {
  const defaultValues = Object.fromEntries(
    fields.map((field) => [field.name, initialValues?.[field.name] ?? ""]),
  );
  const validators = Object.fromEntries(
    fields.map((field) => [
      field.name,
      field.validate ??
        (field.required ? validateRequired(field.label) : noValidate),
    ]),
  );

  const { values, errors, handleChange, handleBlur, validateAll } =
    useFormValidation(defaultValues, validators);

  const handleSubmit = (event) => {
    event.preventDefault();
    const newErrors = validateAll();
    if (hasErrors(newErrors)) return;
    onSubmit(values);
  };

  return (
    <Modal
      title={title}
      subtitle={subtitle}
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
            type="submit"
            form="entity-form-modal"
            disabled={submitting}
            className="rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {submitting ? "Saving…" : submitLabel}
          </button>
        </>
      }
    >
      <form
        id="entity-form-modal"
        onSubmit={handleSubmit}
        noValidate
        className="flex flex-col gap-4"
      >
        {submitError && (
          <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
            {submitError}
          </p>
        )}

        {fields.map((field) => {
          if (field.type === "select") {
            return (
              <div key={field.name}>
                <label className="mb-1.5 block text-label text-muted-700">
                  {field.label}
                </label>
                <select
                  value={values[field.name]}
                  onChange={handleChange(field.name)}
                  onBlur={handleBlur(field.name)}
                  className={`${SELECT_CLASSES} ${errors[field.name] ? "border-danger" : ""}`}
                >
                  <option value="">Select {field.label.toLowerCase()}</option>
                  {field.options.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
                {errors[field.name] && (
                  <span className="mt-1.5 block text-xs text-danger">
                    {errors[field.name]}
                  </span>
                )}
              </div>
            );
          }

          return (
            <FormInput
              key={field.name}
              id={field.name}
              label={field.label}
              type={
                field.type === "textarea" ? undefined : (field.type ?? "text")
              }
              as={field.type === "textarea" ? "textarea" : "input"}
              rows={field.type === "textarea" ? 3 : undefined}
              placeholder={field.placeholder}
              value={values[field.name]}
              onChange={handleChange(field.name)}
              onBlur={handleBlur(field.name)}
              error={errors[field.name]}
            />
          );
        })}

        <div>
          <span className="mb-1.5 block text-label text-muted-700">
            Cover image
          </span>
          <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-muted-400 bg-bg px-4 py-6 text-center">
            <ImagePlus
              size={20}
              aria-hidden="true"
              className="text-muted-500"
            />
            <span className="text-label text-muted-600">
              Click to upload or drag and drop
            </span>
          </div>
        </div>
      </form>
    </Modal>
  );
}

export default EntityFormModal;
