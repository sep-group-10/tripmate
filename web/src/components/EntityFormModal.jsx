import { useRef, useState } from "react";
import { ImagePlus, Trash2 } from "lucide-react";
import Modal from "./Modal";
import FormInput from "./FormInput";
import LocationPicker from "./LocationPicker";
import { useFormValidation, hasErrors } from "../hooks/useFormValidation";
import { validateRequired, validateLocation } from "../utils/validation";
import { parseApiError } from "../utils/apiError";

const ACCEPTED_IMAGE_TYPES = "image/jpeg,image/png,image/webp";

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
 * with a custom one (e.g. numeric range checks for lat/long). `helperText`
 * renders a muted note under the field.
 * A `type: 'location'` field renders LocationPicker instead of a plain
 * input - its value is `{ latitude, longitude } | null`, not a string, and
 * `resolveInitialCenter(values)` lets the caller derive where the map
 * should start (e.g. from whichever destination is currently selected in
 * this same form) from the form's live values.
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
  onUploadPhoto,
  onDeletePhoto,
  submitting = false,
  submitError = "",
}) {
  const defaultValues = Object.fromEntries(
    fields.map((field) => [
      field.name,
      initialValues?.[field.name] ?? (field.type === "location" ? null : ""),
    ]),
  );
  const validators = Object.fromEntries(
    fields.map((field) => [
      field.name,
      field.validate ??
        (field.required
          ? field.type === "location"
            ? validateLocation(field.label)
            : validateRequired(field.label)
          : noValidate),
    ]),
  );

  const { values, errors, setValues, handleChange, handleBlur, validateAll } =
    useFormValidation(defaultValues, validators);

  const fileInputRef = useRef(null);
  const [photoStatus, setPhotoStatus] = useState("idle"); // idle | uploading | error
  const [photoError, setPhotoError] = useState("");
  const [photoUrls, setPhotoUrls] = useState(initialValues?.photo_urls || []);
  const [deletingPhoto, setDeletingPhoto] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    // Photo uploads commit independently. Don't submit a potentially stale
    // edit form while that request is still in flight.
    if (photoStatus === "uploading" || deletingPhoto || submitting) return;
    const newErrors = validateAll();
    if (hasErrors(newErrors)) return;
    onSubmit(values);
  };

  const handlePhotoChange = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setPhotoStatus("uploading");
    setPhotoError("");
    try {
      const updated = await onUploadPhoto(file);
      setPhotoUrls(updated.photo_urls || []);
      setPhotoStatus("idle");
    } catch (error) {
      setPhotoError(parseApiError(error).message);
      setPhotoStatus("error");
    }
  };

  const handlePhotoDelete = async (url) => {
    if (!onDeletePhoto || deletingPhoto) return;
    setDeletingPhoto(url);
    setPhotoError("");
    try {
      const updated = await onDeletePhoto(url);
      setPhotoUrls(updated.photo_urls || []);
    } catch (error) {
      setPhotoError(parseApiError(error).message);
    } finally {
      setDeletingPhoto(null);
    }
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
            disabled={
              submitting || photoStatus === "uploading" || deletingPhoto
            }
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm font-medium text-ink shadow-control disabled:cursor-not-allowed disabled:opacity-70"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="entity-form-modal"
            disabled={
              submitting || photoStatus === "uploading" || deletingPhoto
            }
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
                {field.helperText && (
                  <span className="mt-1.5 block text-xs text-muted-600">
                    {field.helperText}
                  </span>
                )}
              </div>
            );
          }

          if (field.type === "location") {
            return (
              <div key={field.name}>
                <label className="mb-1.5 block text-label text-muted-700">
                  {field.label}
                </label>
                <LocationPicker
                  value={values[field.name]}
                  onChange={(coords) =>
                    setValues((prev) => ({ ...prev, [field.name]: coords }))
                  }
                  initialCenter={field.resolveInitialCenter?.(values)}
                />
                {errors[field.name] && (
                  <span className="mt-1.5 block text-xs text-danger">
                    {errors[field.name]}
                  </span>
                )}
                {field.helperText && (
                  <span className="mt-1.5 block text-xs text-muted-600">
                    {field.helperText}
                  </span>
                )}
              </div>
            );
          }

          return (
            <div key={field.name}>
              <FormInput
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
              {field.helperText && (
                <span className="mt-1.5 block text-xs text-muted-600">
                  {field.helperText}
                </span>
              )}
            </div>
          );
        })}

        {onUploadPhoto && (
          <div>
            <span className="mb-1.5 block text-label text-muted-700">
              Photos
            </span>
            {photoError && (
              <p className="m-0 mb-2 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
                {photoError}
              </p>
            )}

            {photoUrls.length > 0 && (
              <div className="mb-3 grid grid-cols-3 gap-2">
                {photoUrls.map((url) => (
                  <div key={url} className="relative">
                    <img
                      src={url}
                      alt=""
                      className="aspect-square w-full rounded-lg object-cover"
                    />
                    {onDeletePhoto && (
                      <button
                        type="button"
                        onClick={() => handlePhotoDelete(url)}
                        disabled={
                          submitting ||
                          photoStatus === "uploading" ||
                          Boolean(deletingPhoto)
                        }
                        aria-label={`Delete photo${deletingPhoto === url ? ", deleting" : ""}`}
                        title="Delete photo"
                        className="absolute right-1 top-1 flex h-8 w-8 items-center justify-center rounded-full bg-white/95 text-danger shadow-control disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        <Trash2 size={15} aria-hidden="true" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept={ACCEPTED_IMAGE_TYPES}
              onChange={handlePhotoChange}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={
                photoStatus === "uploading" || submitting || deletingPhoto
              }
              className="flex w-full flex-col items-center gap-2 rounded-lg border border-dashed border-muted-400 bg-bg px-4 py-6 text-center disabled:cursor-not-allowed disabled:opacity-70"
            >
              <ImagePlus
                size={20}
                aria-hidden="true"
                className="text-muted-500"
              />
              <span className="text-label text-muted-600">
                {photoStatus === "uploading" ? "Uploading…" : "Add photo"}
              </span>
            </button>
          </div>
        )}
      </form>
    </Modal>
  );
}

export default EntityFormModal;
