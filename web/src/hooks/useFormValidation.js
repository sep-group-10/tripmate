import { useState } from "react";

/** Shared change/blur/validate-on-submit wiring for a form, given a
 * {field: validatorFn} map. One instance per form; screens like Login and
 * Profile can reuse this with their own initial values and validators. */
export function useFormValidation(initialValues, validators) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = (field) => (event) => {
    const { value } = event.target;
    setValues((prev) => ({ ...prev, [field]: value }));
    if (touched[field]) {
      setErrors((prev) => ({ ...prev, [field]: validators[field](value) }));
    }
  };

  const handleBlur = (field) => () => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors((prev) => ({
      ...prev,
      [field]: validators[field](values[field]),
    }));
  };

  const validateAll = () => {
    const newErrors = {};
    for (const field of Object.keys(validators)) {
      newErrors[field] = validators[field](values[field]);
    }
    setErrors(newErrors);
    setTouched(
      Object.keys(validators).reduce(
        (acc, field) => ({ ...acc, [field]: true }),
        {},
      ),
    );
    return newErrors;
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };

  return { values, errors, handleChange, handleBlur, validateAll, reset };
}

export function hasErrors(errorMap) {
  return Object.values(errorMap).some(Boolean);
}
