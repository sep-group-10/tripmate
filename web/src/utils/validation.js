export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function validateFullName(value) {
  if (!value) return "Full name is required";
  if (value.length > 255) return "Full name must be 255 characters or fewer";
  if (!value.trim()) return "Full name cannot be blank or only whitespace";
  return "";
}

export function validateEmail(value) {
  if (!value.trim()) return "Email is required";
  if (!EMAIL_PATTERN.test(value.trim())) return "Enter a valid email address";
  return "";
}

export function validatePassword(value) {
  if (!value) return "Password is required";
  if (value.length < 8) return "Password must be at least 8 characters";
  if (value.length > 72) return "Password must be 72 characters or fewer";
  if (!value.trim()) return "Password cannot be blank or only whitespace";
  return "";
}

export const registerValidators = {
  fullName: validateFullName,
  email: validateEmail,
  password: validatePassword,
};

export function validateLoginPassword(value) {
  if (!value) return "Password is required";
  return "";
}

export const loginValidators = {
  email: validateEmail,
  password: validateLoginPassword,
};

export function validateRequired(label) {
  return (value) =>
    value && value.toString().trim() ? "" : `${label} is required`;
}

// backend/app/schemas/tourism.py's DestinationCreate/Update require
// latitude/longitude as Decimals - these mirror the standard geographic
// range checks (the backend itself doesn't range-check them, but a value
// outside these bounds is never a real coordinate).
export function validateLatitude(value) {
  if (value === "" || value === null || value === undefined) {
    return "Latitude is required";
  }
  const num = Number(value);
  if (Number.isNaN(num)) return "Latitude must be a number";
  if (num < -90 || num > 90) return "Latitude must be between -90 and 90";
  return "";
}

export function validateLongitude(value) {
  if (value === "" || value === null || value === undefined) {
    return "Longitude is required";
  }
  const num = Number(value);
  if (Number.isNaN(num)) return "Longitude must be a number";
  if (num < -180 || num > 180) return "Longitude must be between -180 and 180";
  return "";
}
