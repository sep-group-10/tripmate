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
 * (text/select/textarea) and the required/optional/validate/submit/cancel
 * plumbing are identical. Each field is { name, label, type:
 * 'text'|'select'|'textarea', options?, placeholder?, required? }.
 * Pass `initialValues` (an existing record) to open in edit mode — fields
 * are pre-filled and the caller's onSubmit decides whether that means
 * updating that record or creating a new one; this component doesn't know
 * or care which mode it's in beyond what to pre-fill. */
function EntityFormModal({
  title,
  subtitle,
  submitLabel,
  fields,
  initialValues,
  onSubmit,
  onClose,
}) {
  const defaultValues = Object.fromEntries(
    fields.map((field) => [field.name, initialValues?.[field.name] ?? ""]),
  );
  const validators = Object.fromEntries(
    fields.map((field) => [
      field.name,
      field.required ? validateRequired(field.label) : noValidate,
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
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm font-medium text-ink shadow-control"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="entity-form-modal"
            className="rounded-full bg-accent px-4 py-2 text-sm font-medium text-white shadow-control hover:bg-accent-600 active:bg-accent-700"
          >
            {submitLabel}
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
        {fields.map((field) => {
          if (field.type === "select") {
            return (
              <div key={field.name}>
                <label className="mb-1.5 block text-[13px] text-muted-700">
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
          <span className="mb-1.5 block text-[13px] text-muted-700">
            Cover image
          </span>
          <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-muted-400 bg-bg px-4 py-6 text-center">
            <svg
              width="20"
              height="20"
              viewBox="0 0 256 256"
              fill="currentColor"
              aria-hidden="true"
              className="text-muted-500"
            >
              <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM152,88V44l44,44Z" />
            </svg>
            <span className="text-[13px] text-muted-600">
              Click to upload or drag and drop
            </span>
          </div>
        </div>
      </form>
    </Modal>
  );
}

export default EntityFormModal;
