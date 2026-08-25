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
